from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core.models import (
    User,
    Profile,
    Skill,
    Resume,
    ExtractedInformation,
    ResumeSkill,
    JobDescription,
    JobRequirement,
    JobMatchAnalysis,
    SkillGapAnalysis,
    JobCategory,
    CareerRole,
    CareerRecommendation,
    LearningResource,
    AnalysisHistory,
)

admin.site.site_header = "CareerLens administration"
admin.site.site_title = "CareerLens"
admin.site.register(User, UserAdmin)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ["name", "category"]
    list_filter = ["category"]
    search_fields = ["name"]


@admin.register(CareerRole)
class CareerRoleAdmin(admin.ModelAdmin):
    list_display = ["title", "category"]
    filter_horizontal = ["skills"]


@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ["title", "skill", "level"]
    search_fields = ["title", "skill__name"]


for model in [
    Profile,
    Resume,
    ExtractedInformation,
    ResumeSkill,
    JobDescription,
    JobRequirement,
    JobMatchAnalysis,
    SkillGapAnalysis,
    JobCategory,
    CareerRecommendation,
    AnalysisHistory,
]:
    admin.site.register(model)
