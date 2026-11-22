import json
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.db.models import Avg, Count
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import (
    action,
    api_view,
    permission_classes,
    throttle_classes,
)
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.authtoken.models import Token
from rest_framework import serializers as fields
from drf_spectacular.utils import extend_schema, inline_serializer
from drf_spectacular.types import OpenApiTypes
from core.models import (
    Resume,
    JobDescription,
    JobMatchAnalysis,
    CareerRecommendation,
    AnalysisHistory,
    Skill,
    Profile,
)
from core.serializers import (
    RegisterSerializer,
    AccountSerializer,
    ResumeSerializer,
    ResumeUploadSerializer,
    JobSerializer,
    MatchSerializer,
    CareerSerializer,
    HistorySerializer,
    SkillSerializer,
)
from core.services.analysis import create_match, recommend_careers

SessionSchema = inline_serializer(
    "SessionResponse", fields={"token": fields.CharField(), "user": AccountSerializer()}
)
LoginSchema = inline_serializer(
    "LoginRequest",
    fields={
        "email": fields.EmailField(),
        "password": fields.CharField(write_only=True),
    },
)


class AuthThrottle(AnonRateThrottle):
    scope = "auth"


def session_payload(user):
    Profile.objects.get_or_create(user=user)
    Token.objects.filter(user=user).delete()
    token = Token.objects.create(user=user)
    return {"token": token.key, "user": AccountSerializer(user).data}


def resume_filter(request):
    value = request.query_params.get("resume")
    if value is None:
        return None
    try:
        parsed = int(value)
        if parsed < 1:
            raise ValueError
        return parsed
    except (ValueError, TypeError):
        raise ValidationError({"resume": "Use a positive resume ID."})


@extend_schema(request=RegisterSerializer, responses={201: SessionSchema})
@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AuthThrottle])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user = serializer.save()
    except IntegrityError:
        raise ValidationError({"email": "An account with this email already exists."})
    return Response(session_payload(user), status=status.HTTP_201_CREATED)


@extend_schema(request=LoginSchema, responses=SessionSchema)
@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AuthThrottle])
def login(request):
    email = str(request.data.get("email", "")).strip()
    password = request.data.get("password")
    if not isinstance(password, str) or len(password) > 128:
        raise AuthenticationFailed("Email or password is incorrect.")
    user = get_user_model().objects.filter(email__iexact=email, is_active=True).first()
    if not user:
        get_user_model()().set_password(password)
        raise AuthenticationFailed("Email or password is incorrect.")
    if not user.check_password(password):
        raise AuthenticationFailed("Email or password is incorrect.")
    return Response(session_payload(user))


@extend_schema(request=None, responses=OpenApiTypes.OBJECT)
@api_view(["POST"])
def logout(request):
    request.auth.delete()
    return Response({"message": "Signed out."})


@extend_schema(request=AccountSerializer, responses=AccountSerializer)
@api_view(["GET", "PATCH"])
def me(request):
    Profile.objects.get_or_create(user=request.user)
    if request.method == "PATCH":
        serializer = AccountSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    return Response(AccountSerializer(request.user).data)


@extend_schema(request=None, responses={201: SessionSchema})
@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AuthThrottle])
def demo(request):
    if not settings.DEMO_ENABLED:
        return Response(
            {"error": {"message": "Sample workspaces are disabled."}}, status=404
        )
    from core.services.demo import create_demo_workspace

    return Response(session_payload(create_demo_workspace()), status=201)


class ResumeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Resume.objects.none()
    serializer_class = ResumeSerializer
    search_fields = ["title", "original_filename"]
    ordering_fields = ["created_at", "quality_score", "title"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        return (
            Resume.objects.filter(user=self.request.user)
            .select_related("extracted")
            .prefetch_related("skill_evidence__skill")
        )

    @extend_schema(
        request={"multipart/form-data": ResumeUploadSerializer},
        responses={201: ResumeSerializer},
    )
    def create(self, request):
        serializer = ResumeUploadSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(ResumeSerializer(serializer.save()).data, status=201)

    def destroy(self, request, pk=None):
        self.get_object().delete()
        return Response(status=204)

    @extend_schema(responses=OpenApiTypes.BINARY)
    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        resume = self.get_object()
        response = FileResponse(
            resume.file.open("rb"),
            as_attachment=True,
            filename=resume.original_filename,
        )
        response["Cache-Control"] = "no-store"
        return response

    @action(detail=True, methods=["get"])
    def report(self, request, pk=None):
        response = HttpResponse(
            json.dumps(ResumeSerializer(self.get_object()).data, indent=2),
            content_type="application/json",
        )
        response["Content-Disposition"] = (
            'attachment; filename="careerlens-resume-report.json"'
        )
        response["Cache-Control"] = "no-store"
        return response

    @extend_schema(
        request=inline_serializer(
            "RecommendationRequest",
            fields={"use_ai": fields.BooleanField(default=False)},
        ),
        responses={201: CareerSerializer(many=True)},
    )
    @action(detail=True, methods=["post"])
    def recommend(self, request, pk=None):
        use_ai = request.data.get("use_ai", False)
        if not isinstance(use_ai, bool):
            raise ValidationError({"use_ai": "Use a boolean value."})
        recommendations = recommend_careers(self.get_object(), use_ai=use_ai)
        return Response(CareerSerializer(recommendations, many=True).data, status=201)


class JobViewSet(viewsets.ModelViewSet):
    queryset = JobDescription.objects.none()
    serializer_class = JobSerializer
    search_fields = ["title", "company", "description"]
    ordering_fields = ["created_at", "title"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        return JobDescription.objects.filter(user=self.request.user).prefetch_related(
            "requirements__skill"
        )


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = JobMatchAnalysis.objects.none()
    serializer_class = MatchSerializer
    search_fields = ["resume__title", "job__title"]
    ordering_fields = ["created_at", "score"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        query = JobMatchAnalysis.objects.filter(user=self.request.user).select_related(
            "resume", "job"
        )
        resume_id = resume_filter(self.request)
        if resume_id is not None:
            query = query.filter(resume_id=resume_id)
        return query

    @extend_schema(
        request=inline_serializer(
            "MatchRequest",
            fields={
                "resume": fields.IntegerField(min_value=1),
                "job": fields.IntegerField(min_value=1),
            },
        ),
        responses={201: MatchSerializer},
    )
    def create(self, request):
        try:
            resume_id, job_id = (
                int(request.data.get("resume", 0)),
                int(request.data.get("job", 0)),
            )
        except (TypeError, ValueError):
            raise ValidationError("Choose a resume and a job description.")
        resume = get_object_or_404(
            Resume.objects.select_related("extracted"), pk=resume_id, user=request.user
        )
        job = get_object_or_404(JobDescription, pk=job_id, user=request.user)
        if not job.requirements.exists():
            raise ValidationError(
                "Add at least one skill requirement to this job before comparing."
            )
        return Response(
            MatchSerializer(create_match(request.user, resume, job)).data, status=201
        )


class CareerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CareerRecommendation.objects.none()
    serializer_class = CareerSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        query = CareerRecommendation.objects.filter(
            resume__user=self.request.user
        ).select_related("role", "resume")
        resume_id = resume_filter(self.request)
        if resume_id is not None:
            query = query.filter(resume_id=resume_id)
        return query


class HistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AnalysisHistory.objects.none()
    serializer_class = HistorySerializer
    search_fields = ["title", "kind"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        return AnalysisHistory.objects.filter(user=self.request.user)


@extend_schema(responses=SkillSerializer(many=True))
@api_view(["GET"])
def skills(request):
    return Response(
        SkillSerializer(Skill.objects.all().order_by("name"), many=True).data
    )


@extend_schema(responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
def dashboard(request):
    resumes = Resume.objects.filter(user=request.user)
    matches = JobMatchAnalysis.objects.filter(user=request.user).select_related(
        "job", "resume"
    )
    top_skills = (
        Skill.objects.filter(resumeskill__resume__user=request.user)
        .annotate(count=Count("resumeskill"))
        .order_by("-count", "name")[:8]
    )
    gaps = {}
    for match in matches[:20]:
        for gap in match.result.get("gaps", []):
            gaps[gap["name"]] = gaps.get(gap["name"], 0) + 1
    trend = [
        {
            "label": m.created_at.strftime("%d %b"),
            "job": m.result.get("job_snapshot", {}).get("title", m.job.title),
            "score": m.score,
        }
        for m in reversed(list(matches[:10]))
    ]
    careers = CareerRecommendation.objects.filter(
        resume__user=request.user
    ).select_related("role", "resume")
    return Response(
        {
            "total_resumes": resumes.count(),
            "average_quality": round(
                resumes.aggregate(avg=Avg("quality_score"))["avg"] or 0, 1
            ),
            "total_jobs": JobDescription.objects.filter(user=request.user).count(),
            "analyzed_jobs": matches.values("job_id").distinct().count(),
            "total_matches": matches.count(),
            "average_match": round(matches.aggregate(avg=Avg("score"))["avg"] or 0, 1),
            "top_skills": [
                {"name": s.name, "category": s.category, "count": s.count}
                for s in top_skills
            ],
            "missing_skills": [
                {"name": k, "count": v}
                for k, v in sorted(gaps.items(), key=lambda x: -x[1])[:6]
            ],
            "trend": trend,
            "recent_matches": MatchSerializer(matches[:4], many=True).data,
            "recent_resumes": ResumeSerializer(
                resumes.select_related("extracted").prefetch_related(
                    "skill_evidence__skill"
                )[:3],
                many=True,
            ).data,
            "careers": CareerSerializer(
                sorted(list(careers[:4]), key=lambda c: c.score, reverse=True),
                many=True,
            ).data,
            "history": HistorySerializer(
                AnalysisHistory.objects.filter(user=request.user)[:6], many=True
            ).data,
            "provider_configured": bool(
                settings.LLM_API_KEY and settings.LLM_BASE_URL and settings.LLM_MODEL
            ),
            "engine": "rule-based-v1",
            "sample_workspace": request.user.username.startswith("sample-"),
        }
    )


@extend_schema(responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
@permission_classes([IsAdminUser])
def system_stats(request):
    return Response(
        {
            "users": get_user_model().objects.count(),
            "resumes": Resume.objects.count(),
            "jobs": JobDescription.objects.count(),
            "matches": JobMatchAnalysis.objects.count(),
            "skills": Skill.objects.count(),
            "activity": list(
                AnalysisHistory.objects.values("kind")
                .annotate(count=Count("id"))
                .order_by("-count")
            ),
        }
    )
