import uuid
from pathlib import Path
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

score_validators = [MinValueValidator(0), MaxValueValidator(100)]


class User(AbstractUser):
    email = models.EmailField(unique=True)


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    headline = models.CharField(max_length=160, blank=True)
    location = models.CharField(max_length=120, blank=True)
    career_goal = models.CharField(max_length=240, blank=True)


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=15,
        choices=[("technical", "Technical"), ("soft", "Soft"), ("tool", "Tool")],
    )
    aliases = models.JSONField(default=list, blank=True)
    related_skills = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.name


def resume_path(instance, filename):
    return (
        f"resumes/{instance.user_id}/{uuid.uuid4().hex}{Path(filename).suffix.lower()}"
    )


class Resume(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resumes"
    )
    title = models.CharField(max_length=160)
    file = models.FileField(upload_to=resume_path)
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    quality_score = models.PositiveSmallIntegerField(
        validators=score_validators, default=0
    )
    quality_report = models.JSONField(default=dict)
    skills = models.ManyToManyField(Skill, through="ResumeSkill")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]


class ExtractedInformation(models.Model):
    resume = models.OneToOneField(
        Resume, on_delete=models.CASCADE, related_name="extracted"
    )
    text = models.TextField()
    candidate_name = models.CharField(max_length=160, blank=True)
    email = models.CharField(max_length=254, blank=True)
    phone = models.CharField(max_length=60, blank=True)
    sections = models.JSONField(default=dict)
    experience_years = models.FloatField(null=True, blank=True)
    warnings = models.JSONField(default=list)


class ResumeSkill(models.Model):
    resume = models.ForeignKey(
        Resume, on_delete=models.CASCADE, related_name="skill_evidence"
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    evidence = models.CharField(max_length=500)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["resume", "skill"], name="unique_resume_skill"
            )
        ]


class JobCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class JobDescription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="jobs"
    )
    title = models.CharField(max_length=160)
    company = models.CharField(max_length=160, blank=True)
    description = models.TextField(max_length=30000)
    experience_years = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(60)]
    )
    qualification = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class JobRequirement(models.Model):
    job = models.ForeignKey(
        JobDescription, on_delete=models.CASCADE, related_name="requirements"
    )
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT)
    importance = models.CharField(
        max_length=12,
        choices=[("essential", "Essential"), ("preferred", "Preferred")],
        default="essential",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["job", "skill"], name="unique_job_skill")
        ]


class JobMatchAnalysis(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="matches")
    job = models.ForeignKey(
        JobDescription, on_delete=models.CASCADE, related_name="matches"
    )
    score = models.FloatField(validators=score_validators)
    result = models.JSONField()
    engine = models.CharField(max_length=40, default="rule-based-v1")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]


class SkillGapAnalysis(models.Model):
    match = models.OneToOneField(
        JobMatchAnalysis, on_delete=models.CASCADE, related_name="skill_gap"
    )
    gaps = models.JSONField(default=list)
    roadmap = models.JSONField(default=list)


class CareerRole(models.Model):
    title = models.CharField(max_length=120, unique=True)
    description = models.TextField()
    category = models.ForeignKey(
        JobCategory, on_delete=models.SET_NULL, null=True, blank=True
    )
    skills = models.ManyToManyField(Skill)

    def __str__(self):
        return self.title


class LearningResource(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="resources")
    title = models.CharField(max_length=180)
    url = models.URLField()
    level = models.CharField(max_length=40, default="Beginner")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["skill", "url"], name="unique_skill_resource"
            )
        ]


class CareerRecommendation(models.Model):
    resume = models.ForeignKey(
        Resume, on_delete=models.CASCADE, related_name="recommendations"
    )
    role = models.ForeignKey(CareerRole, on_delete=models.CASCADE)
    score = models.FloatField(validators=score_validators)
    result = models.JSONField()
    engine = models.CharField(max_length=40, default="rule-based-v1")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class AnalysisHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="history"
    )
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, null=True, blank=True)
    match = models.ForeignKey(
        JobMatchAnalysis, on_delete=models.CASCADE, null=True, blank=True
    )
    kind = models.CharField(max_length=30)
    title = models.CharField(max_length=240)
    score = models.FloatField(null=True, blank=True)
    detail = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]


@receiver(post_delete, sender=Resume)
def remove_original_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)
