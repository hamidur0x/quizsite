from django.contrib import admin
from .models import AllowedEmail, Quiz, Question, QuizAttempt, AnswerRecord


@admin.register(AllowedEmail)
class AllowedEmailAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "has_attempted", "allow_retake", "created_at")
    search_fields = ("email", "name")
    list_filter = ("has_attempted", "allow_retake")


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = (
        "order", "text",
        "option_a", "option_b", "option_c", "option_d",
        "correct_option", "marks",
    )


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "duration_minutes", "total_marks", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title",)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "quiz", "text", "correct_option", "marks", "order")
    list_filter = ("quiz",)
    search_fields = ("text",)


class AnswerRecordInline(admin.TabularInline):
    model = AnswerRecord
    extra = 0
    readonly_fields = ("question", "selected_option", "is_correct")
    can_delete = False


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("email", "quiz", "score", "total_marks", "percentage", "submitted_at")
    list_filter = ("quiz",)
    search_fields = ("email",)
    readonly_fields = ("email", "quiz", "score", "total_marks", "started_at", "submitted_at")
    inlines = [AnswerRecordInline]
