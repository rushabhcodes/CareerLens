from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from core.models import (
    Profile,
    Skill,
    Resume,
    ExtractedInformation,
    ResumeSkill,
    JobDescription,
    JobRequirement,
    JobMatchAnalysis,
    CareerRecommendation,
    AnalysisHistory,
)
from core.services.parsing import (
    extract_file,
    parse_information,
    identify_skills,
    quality_report,
)

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField(max_length=150)
    password = serializers.CharField(write_only=True, max_length=128)

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        return value

    def validate(self, attrs):
        candidate = User(
            email=attrs["email"],
            username=attrs["email"],
            first_name=attrs["first_name"],
        )
        validate_password(attrs["password"], candidate)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"], **validated_data
        )
        Profile.objects.create(user=user)
        return user


class AccountSerializer(serializers.ModelSerializer):
    headline = serializers.CharField(
        source="profile.headline", max_length=160, required=False, allow_blank=True
    )
    location = serializers.CharField(
        source="profile.location", max_length=120, required=False, allow_blank=True
    )
    career_goal = serializers.CharField(
        source="profile.career_goal", max_length=240, required=False, allow_blank=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "headline",
            "location",
            "career_goal",
        ]
        read_only_fields = ["id", "email", "is_staff"]

    @transaction.atomic
    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        profile, _ = Profile.objects.get_or_create(user=instance)
        for key, value in profile_data.items():
            setattr(profile, key, value)
        profile.save()
        return super().update(instance, validated_data)


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name", "category"]


class ExtractedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedInformation
        exclude = ["id", "resume"]


class ResumeSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)

    class Meta:
        model = ResumeSkill
        fields = ["skill", "evidence"]


class ResumeSerializer(serializers.ModelSerializer):
    extracted = ExtractedSerializer(read_only=True)
    skill_evidence = ResumeSkillSerializer(many=True, read_only=True)

    class Meta:
        model = Resume
        fields = [
            "id",
            "title",
            "original_filename",
            "file_size",
            "quality_score",
            "quality_report",
            "created_at",
            "extracted",
            "skill_evidence",
        ]
        read_only_fields = fields


class ResumeUploadSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=160, required=False, allow_blank=True)
    file = serializers.FileField()

    def validate(self, attrs):
        attrs["text"] = extract_file(attrs["file"])
        return attrs

    def create(self, validated_data):
        upload = validated_data["file"]
        text = validated_data["text"]
        info = parse_information(text)
        skills = identify_skills(text)
        report = quality_report(text, info, len(skills))
        resume = None
        try:
            with transaction.atomic():
                resume = Resume.objects.create(
                    user=self.context["request"].user,
                    title=validated_data.get("title") or upload.name[:160],
                    file=upload,
                    original_filename=upload.name[:255],
                    file_size=upload.size,
                    quality_score=report["score"],
                    quality_report=report,
                )
                ExtractedInformation.objects.create(resume=resume, text=text, **info)
                ResumeSkill.objects.bulk_create(
                    [
                        ResumeSkill(resume=resume, skill=skill, evidence=evidence)
                        for skill, evidence in skills
                    ]
                )
                AnalysisHistory.objects.create(
                    user=resume.user,
                    resume=resume,
                    kind="resume",
                    title=f"Resume review · {resume.title}",
                    score=resume.quality_score,
                )
            return resume
        except Exception:
            if resume and resume.file:
                resume.file.delete(save=False)
            raise


class RequirementSerializer(serializers.ModelSerializer):
    skill = serializers.PrimaryKeyRelatedField(queryset=Skill.objects.all())
    name = serializers.CharField(source="skill.name", read_only=True)
    category = serializers.CharField(source="skill.category", read_only=True)

    class Meta:
        model = JobRequirement
        fields = ["skill", "name", "category", "importance"]


class JobSerializer(serializers.ModelSerializer):
    requirements = RequirementSerializer(many=True, required=False)

    class Meta:
        model = JobDescription
        fields = [
            "id",
            "title",
            "company",
            "description",
            "experience_years",
            "qualification",
            "requirements",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_description(self, value):
        if len(value.strip()) < 30:
            raise serializers.ValidationError(
                "Enter at least 30 characters so the job has useful context."
            )
        return value

    def validate(self, attrs):
        reqs = attrs.get("requirements")
        if reqs is not None and len({r["skill"].pk for r in reqs}) != len(reqs):
            raise serializers.ValidationError(
                {"requirements": "Choose each skill only once."}
            )
        if reqs is None and ("description" in attrs):
            attrs["requirements"] = [
                {"skill": skill, "importance": "essential"}
                for skill, _ in identify_skills(attrs["description"])
            ]
        if "requirements" in attrs and not attrs["requirements"]:
            raise serializers.ValidationError(
                {
                    "requirements": "Select at least one skill, or mention a catalog skill in the description."
                }
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        reqs = validated_data.pop("requirements", [])
        job = JobDescription.objects.create(
            user=self.context["request"].user, **validated_data
        )
        JobRequirement.objects.bulk_create(
            [JobRequirement(job=job, **req) for req in reqs]
        )
        return job

    @transaction.atomic
    def update(self, instance, validated_data):
        reqs = validated_data.pop("requirements", None)
        instance = super().update(instance, validated_data)
        if reqs is not None:
            instance.requirements.all().delete()
            JobRequirement.objects.bulk_create(
                [JobRequirement(job=instance, **req) for req in reqs]
            )
        return instance


class MatchSerializer(serializers.ModelSerializer):
    resume_title = serializers.CharField(source="resume.title", read_only=True)
    job_title = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()

    def get_job_title(self, obj) -> str:
        return obj.result.get("job_snapshot", {}).get("title", obj.job.title)

    def get_company(self, obj) -> str:
        return obj.result.get("job_snapshot", {}).get("company", obj.job.company)

    class Meta:
        model = JobMatchAnalysis
        fields = [
            "id",
            "resume",
            "resume_title",
            "job",
            "job_title",
            "company",
            "score",
            "engine",
            "result",
            "created_at",
        ]
        read_only_fields = fields


class CareerSerializer(serializers.ModelSerializer):
    role_title = serializers.CharField(source="role.title", read_only=True)
    description = serializers.CharField(source="role.description", read_only=True)
    resume_title = serializers.CharField(source="resume.title", read_only=True)

    class Meta:
        model = CareerRecommendation
        fields = [
            "id",
            "resume",
            "resume_title",
            "role_title",
            "description",
            "score",
            "result",
            "engine",
            "created_at",
        ]


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisHistory
        fields = ["id", "resume", "kind", "title", "score", "detail", "created_at"]
