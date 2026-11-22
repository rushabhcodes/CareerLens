import re
from django.db import transaction
from core.models import (
    JobMatchAnalysis,
    SkillGapAnalysis,
    CareerRole,
    CareerRecommendation,
    LearningResource,
    AnalysisHistory,
)


def roadmap_for(gaps):
    steps = []
    for index, gap in enumerate(gaps):
        resources = list(
            LearningResource.objects.filter(skill_id=gap["skill_id"]).values(
                "title", "url", "level"
            )
        )
        steps.append(
            {
                **gap,
                "step": index + 1,
                "action": f"Learn the fundamentals of {gap['name']}, then add a small demonstrable project to your portfolio.",
                "milestone": f"Explain one project decision using {gap['name']} and link to your work.",
                "resources": resources,
            }
        )
    return steps


def calculate_match(resume, job):
    evidence = {
        row.skill_id: row for row in resume.skill_evidence.select_related("skill")
    }
    matched, partial, missing = [], [], []
    earned, total = 0, 0
    requirements = list(
        job.requirements.select_related("skill").prefetch_related(
            "skill__related_skills"
        )
    )
    for req in requirements:
        weight = 2 if req.importance == "essential" else 1
        total += weight
        item = {
            "skill_id": req.skill_id,
            "name": req.skill.name,
            "category": req.skill.category,
            "importance": req.importance,
            "weight": weight,
        }
        if req.skill_id in evidence:
            earned += weight
            matched.append({**item, "evidence": evidence[req.skill_id].evidence})
        else:
            related = [
                row
                for pk, row in evidence.items()
                if pk in {s.pk for s in req.skill.related_skills.all()}
            ]
            if related:
                earned += weight * 0.5
                partial.append(
                    {
                        **item,
                        "related_skill": related[0].skill.name,
                        "explanation": f"{related[0].skill.name} is related in the catalog. It earns half credit and does not prove {req.skill.name} proficiency.",
                    }
                )
            else:
                missing.append(item)
    components = []
    if total:
        skill_value = 100 * earned / total
        components.append(
            {
                "name": "Skills",
                "weight": 70,
                "value": round(skill_value, 2),
                "explanation": f"{earned:g}/{total:g} weighted points. Essential = 2, preferred = 1; explicit = full, related = half, missing = zero.",
            }
        )
    years = resume.extracted.experience_years
    exp_status = "Not requested"
    if job.experience_years is not None:
        exp_value = (
            100
            if job.experience_years == 0
            else min(100, (years or 0) / job.experience_years * 100)
        )
        exp_status = (
            f"{years:g} years explicitly stated; {job.experience_years:g} requested."
            if years is not None
            else "Unknown: resume does not explicitly state experience years. Zero credit until documented."
        )
        components.append(
            {
                "name": "Experience",
                "weight": 20,
                "value": round(exp_value, 2),
                "explanation": exp_status
                + " Credit = min(documented / requested, 1) × 100.",
            }
        )
    education = resume.extracted.sections.get("education", "")
    qualification_status = "Not requested"
    if job.qualification:
        phrase = re.sub(r"\s+", " ", job.qualification.casefold()).strip()
        education_normalized = re.sub(r"\s+", " ", education.casefold())
        present = phrase in education_normalized
        qualification_status = f"Exact qualification phrase {job.qualification!r} " + (
            "appears in the education section."
            if present
            else "was not found in the education section. Review manually for equivalent qualifications."
        )
        components.append(
            {
                "name": "Qualification",
                "weight": 10,
                "value": 100 if present else 0,
                "explanation": qualification_status,
            }
        )
    weight_sum = sum(c["weight"] for c in components)
    score = (
        round(sum(c["value"] * c["weight"] for c in components) / weight_sum, 1)
        if weight_sum
        else 0
    )
    gaps = sorted(
        missing + [{**item, "partial": True} for item in partial],
        key=lambda x: x["importance"] != "essential",
    )
    return {
        "score": score,
        "matched": matched,
        "partial": partial,
        "missing": missing,
        "components": components,
        "experience": exp_status,
        "qualification": qualification_status,
        "education_evidence": education,
        "experience_evidence": resume.extracted.sections.get("experience", ""),
        "formula": "Sum(component value × component weight) / sum(active weights). Skills 70, experience 20, qualification 10. Unrequested components are excluded and active weights are renormalized.",
        "active_weight": weight_sum,
        "disclaimer": "This measures documented alignment with the saved requirements. It is not a probability of getting hired.",
        "job_snapshot": {
            "title": job.title,
            "company": job.company,
            "description": job.description,
            "experience_years": job.experience_years,
            "qualification": job.qualification,
        },
        "gaps": gaps,
        "roadmap": roadmap_for(gaps),
        "engine": "rule-based-v1",
    }


@transaction.atomic
def create_match(user, resume, job):
    result = calculate_match(resume, job)
    match = JobMatchAnalysis.objects.create(
        user=user, resume=resume, job=job, score=result["score"], result=result
    )
    SkillGapAnalysis.objects.create(
        match=match, gaps=result["gaps"], roadmap=result["roadmap"]
    )
    AnalysisHistory.objects.create(
        user=user,
        resume=resume,
        match=match,
        kind="job_match",
        title=f"{resume.title} · {job.title}",
        score=match.score,
        detail={"match_id": match.pk},
    )
    return match


@transaction.atomic
def recommend_careers(resume, use_ai=False):
    from .provider import enrich_advice

    own = set(resume.skills.values_list("pk", flat=True))
    ranked = []
    for role in CareerRole.objects.prefetch_related("skills"):
        skills = list(role.skills.all())
        matched = [s.name for s in skills if s.pk in own]
        if not matched or not skills:
            continue
        gaps = [
            {
                "skill_id": s.pk,
                "name": s.name,
                "category": s.category,
                "importance": "essential",
            }
            for s in skills
            if s.pk not in own
        ]
        ranked.append((round(100 * len(matched) / len(skills), 1), role, matched, gaps))
    ranked.sort(key=lambda item: (-item[0], item[1].title))
    output = []
    for score, role, matched, gaps in ranked[:4]:
        result = {
            "matched_skills": matched,
            "missing_skills": [g["name"] for g in gaps],
            "roadmap": roadmap_for(gaps),
            "reason": f"Your resume explicitly mentions {', '.join(matched)}. These cover {len(matched)} of {len(matched) + len(gaps)} skills in the {role.title} catalog.",
            "formula": "Role coverage = explicitly matched catalog skills / all skills for the role × 100. This is skill overlap, not job readiness or a hiring probability.",
            "experience_note": "Role ranking uses documented skills. Seniority is not inferred from an overlap score.",
            "advice": [],
            "provider_status": "Local analysis requested.",
        }
        engine = "rule-based-v1"
        if use_ai:
            enrichment = enrich_advice(
                {
                    "role": role.title,
                    "documented_skills": matched,
                    "missing_skills": result["missing_skills"],
                }
            )
            result.update(enrichment)
            if enrichment.get("advice"):
                engine = "llm-enriched-v1"
        output.append(
            CareerRecommendation.objects.create(
                resume=resume, role=role, score=score, result=result, engine=engine
            )
        )
    AnalysisHistory.objects.create(
        user=resume.user,
        resume=resume,
        kind="career",
        title=f"Career pathways · {resume.title}",
        detail={"count": len(output)},
    )
    return output
