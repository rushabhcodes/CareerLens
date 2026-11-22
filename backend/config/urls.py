from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from core import views

router = DefaultRouter()
router.register("resumes", views.ResumeViewSet, basename="resume")
router.register("jobs", views.JobViewSet, basename="job")
router.register("matches", views.MatchViewSet, basename="match")
router.register("careers", views.CareerViewSet, basename="career")
router.register("history", views.HistoryViewSet, basename="history")

urlpatterns = [
    path(settings.ADMIN_PATH, admin.site.urls),
    path("api/auth/register/", views.register),
    path("api/auth/login/", views.login),
    path("api/auth/logout/", views.logout),
    path("api/auth/me/", views.me),
    path("api/auth/demo/", views.demo),
    path("api/dashboard/", views.dashboard),
    path("api/skills/", views.skills),
    path("api/system/", views.system_stats),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/", include(router.urls)),
]
