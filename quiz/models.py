from django.db import models
from django.core.validators import MinValueValidator


class AllowedEmail(models.Model):
    """Only emails added here are allowed to take the quiz."""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150, blank=True)
    has_attempted = models.BooleanField(default=False)
    allow_retake = models.BooleanField(
        default=False, help_text="Check this to let the user attempt the quiz again."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Quiz(models.Model):
    """A quiz paper - a collection of questions."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(
        default=30, help_text="Time limit in minutes."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def total_marks(self):
        return sum(q.marks for q in self.questions.all())


class Question(models.Model):
    OPTION_CHOICES = (
        ("A", "Option A"),
        ("B", "Option B"),
        ("C", "Option C"),
        ("D", "Option D"),
    )

    quiz = models.ForeignKey(Quiz, related_name="questions", on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Question")
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500, blank=True)
    option_d = models.CharField(max_length=500, blank=True)
    correct_option = models.CharField(
        max_length=1, choices=OPTION_CHOICES,
        help_text="Define the correct answer for this question here."
    )
    marks = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}: {self.text[:50]}"

    def options(self):
        opts = []
        for key, label in self.OPTION_CHOICES:
            value = getattr(self, f"option_{key.lower()}")
            if value:
                opts.append((key, value))
        return opts


class QuizAttempt(models.Model):
    """One submission/attempt of a quiz by an allowed email."""
    email = models.EmailField()
    quiz = models.ForeignKey(Quiz, related_name="attempts", on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    total_marks = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.email} - {self.quiz.title} - {self.score}/{self.total_marks}"

    @property
    def percentage(self):
        if self.total_marks == 0:
            return 0
        return round((self.score / self.total_marks) * 100, 2)


class AnswerRecord(models.Model):
    """Stores what the candidate selected for each question."""
    attempt = models.ForeignKey(QuizAttempt, related_name="answers", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, blank=True)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ("attempt", "question")

    def __str__(self):
        return f"{self.attempt.email} - Q{self.question_id} - {self.selected_option}"
