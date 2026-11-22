from core.models import Skill, CareerRole, JobCategory, LearningResource

# This is a vocabulary and career catalog, not fabricated user activity.
CATALOG = {
    "Python": ("technical", ["python3"], "https://docs.python.org/3/tutorial/"),
    "JavaScript": (
        "technical",
        ["javascript", "js", "ecmascript"],
        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
    ),
    "TypeScript": (
        "technical",
        ["typescript", "ts"],
        "https://www.typescriptlang.org/docs/",
    ),
    "Java": ("technical", [], "https://dev.java/learn/"),
    "C++": ("technical", ["cpp"], "https://isocpp.org/get-started"),
    "C#": ("technical", ["csharp"], "https://learn.microsoft.com/en-us/dotnet/csharp/"),
    "React": ("technical", ["react.js", "reactjs"], "https://react.dev/learn"),
    "Django": (
        "technical",
        ["django rest framework", "drf"],
        "https://docs.djangoproject.com/en/5.2/intro/",
    ),
    "Flask": ("technical", [], "https://flask.palletsprojects.com/en/stable/tutorial/"),
    "Node.js": ("technical", ["nodejs", "node.js"], "https://nodejs.org/en/learn"),
    "HTML": (
        "technical",
        ["html5"],
        "https://developer.mozilla.org/en-US/docs/Learn_web_development",
    ),
    "CSS": (
        "technical",
        ["css3", "tailwind", "tailwind css"],
        "https://developer.mozilla.org/en-US/docs/Web/CSS",
    ),
    "SQL": (
        "technical",
        [],
        "https://www.postgresql.org/docs/current/tutorial-sql.html",
    ),
    "MySQL": ("tool", [], "https://dev.mysql.com/doc/"),
    "PostgreSQL": (
        "tool",
        ["postgres"],
        "https://www.postgresql.org/docs/current/tutorial.html",
    ),
    "MongoDB": ("tool", ["mongo"], "https://www.mongodb.com/docs/"),
    "Git": ("tool", ["version control"], "https://git-scm.com/book/en/v2"),
    "Docker": ("tool", ["containerization"], "https://docs.docker.com/get-started/"),
    "Kubernetes": ("tool", ["k8s"], "https://kubernetes.io/docs/tutorials/"),
    "AWS": ("tool", ["amazon web services"], "https://aws.amazon.com/training/"),
    "Azure": (
        "tool",
        ["microsoft azure"],
        "https://learn.microsoft.com/en-us/training/azure/",
    ),
    "Linux": ("tool", [], "https://linuxjourney.com/"),
    "REST APIs": (
        "technical",
        ["rest api", "restful", "rest apis"],
        "https://developer.mozilla.org/en-US/docs/Glossary/REST",
    ),
    "GraphQL": ("technical", [], "https://graphql.org/learn/"),
    "Testing": (
        "technical",
        ["unit testing", "pytest", "jest", "vitest", "automated testing"],
        "https://docs.pytest.org/en/stable/getting-started.html",
    ),
    "CI/CD": (
        "technical",
        ["continuous integration", "github actions"],
        "https://docs.github.com/en/actions",
    ),
    "Data structures": (
        "technical",
        ["data structures and algorithms", "dsa"],
        "https://ocw.mit.edu/",
    ),
    "Machine learning": (
        "technical",
        ["scikit-learn", "machine learning"],
        "https://scikit-learn.org/stable/tutorial/",
    ),
    "NLP": (
        "technical",
        ["natural language processing", "spacy"],
        "https://spacy.io/usage/spacy-101",
    ),
    "TensorFlow": ("tool", [], "https://www.tensorflow.org/tutorials"),
    "PyTorch": ("tool", [], "https://pytorch.org/tutorials/"),
    "Pandas": ("tool", [], "https://pandas.pydata.org/docs/getting_started/"),
    "NumPy": ("tool", [], "https://numpy.org/learn/"),
    "Data analysis": (
        "technical",
        ["data analytics"],
        "https://pandas.pydata.org/docs/getting_started/",
    ),
    "Statistics": (
        "technical",
        ["statistical analysis"],
        "https://www.khanacademy.org/math/statistics-probability",
    ),
    "Excel": ("tool", ["microsoft excel"], "https://support.microsoft.com/en-us/excel"),
    "Power BI": ("tool", ["powerbi"], "https://learn.microsoft.com/en-us/power-bi/"),
    "Tableau": ("tool", [], "https://www.tableau.com/learn/training"),
    "Figma": ("tool", [], "https://help.figma.com/"),
    "UI/UX": (
        "technical",
        ["user experience", "ux design", "ui design"],
        "https://www.w3.org/WAI/tutorials/",
    ),
    "Accessibility": (
        "technical",
        ["wcag", "a11y"],
        "https://www.w3.org/WAI/tutorials/",
    ),
    "Communication": (
        "soft",
        ["communication skills", "written communication"],
        "https://www.open.edu/openlearn/",
    ),
    "Teamwork": (
        "soft",
        ["team collaboration", "collaboration", "team player"],
        "https://www.open.edu/openlearn/",
    ),
    "Leadership": (
        "soft",
        ["team leadership", "mentoring"],
        "https://www.open.edu/openlearn/",
    ),
    "Problem solving": (
        "soft",
        ["problem-solving", "problem solving"],
        "https://www.open.edu/openlearn/",
    ),
    "Time management": ("soft", ["time-management"], "https://www.open.edu/openlearn/"),
    "Agile": ("soft", ["scrum", "agile methodology"], "https://scrumguides.org/"),
    "Spring Boot": ("technical", ["springboot"], "https://spring.io/guides"),
    "Redis": ("tool", [], "https://redis.io/docs/latest/"),
    "Security": (
        "technical",
        ["cybersecurity", "application security", "owasp"],
        "https://owasp.org/www-project-top-ten/",
    ),
}

ROLES = {
    "Full-stack developer": [
        "JavaScript",
        "React",
        "Python",
        "Django",
        "SQL",
        "Git",
        "REST APIs",
        "Testing",
    ],
    "Frontend developer": [
        "JavaScript",
        "TypeScript",
        "React",
        "HTML",
        "CSS",
        "Accessibility",
        "Git",
    ],
    "Python backend developer": [
        "Python",
        "Django",
        "SQL",
        "REST APIs",
        "Docker",
        "Testing",
        "Git",
    ],
    "Data analyst": [
        "Python",
        "SQL",
        "Pandas",
        "Excel",
        "Data analysis",
        "Statistics",
        "Communication",
    ],
    "Machine learning engineer": [
        "Python",
        "Machine learning",
        "Statistics",
        "NumPy",
        "Pandas",
        "PyTorch",
        "NLP",
    ],
    "DevOps engineer": [
        "Linux",
        "Docker",
        "Kubernetes",
        "AWS",
        "CI/CD",
        "Git",
        "Python",
    ],
    "Java backend developer": [
        "Java",
        "Spring Boot",
        "SQL",
        "REST APIs",
        "Git",
        "Testing",
    ],
    "UX engineer": [
        "Figma",
        "UI/UX",
        "Accessibility",
        "HTML",
        "CSS",
        "JavaScript",
        "Communication",
    ],
}


def seed_catalog():
    for name, (category, aliases, url) in CATALOG.items():
        skill, _ = Skill.objects.get_or_create(
            name=name, defaults={"category": category, "aliases": aliases}
        )
        LearningResource.objects.get_or_create(
            skill=skill, url=url, defaults={"title": f"{name} learning guide"}
        )
    for first, second in [
        ("JavaScript", "TypeScript"),
        ("MySQL", "PostgreSQL"),
        ("SQL", "MySQL"),
        ("SQL", "PostgreSQL"),
    ]:
        first_skill, second_skill = (
            Skill.objects.get(name=first),
            Skill.objects.get(name=second),
        )
        relation = Skill.related_skills.through
        # Connector/Python can surface duplicate INSERT IGNORE warnings as errors.
        # Explicit unique-pair lookups keep repeated bootstrap runs idempotent.
        relation.objects.get_or_create(
            from_skill_id=first_skill.pk, to_skill_id=second_skill.pk
        )
        relation.objects.get_or_create(
            from_skill_id=second_skill.pk, to_skill_id=first_skill.pk
        )
    category, _ = JobCategory.objects.get_or_create(name="Technology")
    for title, names in ROLES.items():
        role, created = CareerRole.objects.get_or_create(
            title=title,
            defaults={
                "category": category,
                "description": f"Build a portfolio demonstrating the core skills used by a {title.lower()}.",
            },
        )
        if created:
            role.skills.set(Skill.objects.filter(name__in=names))
