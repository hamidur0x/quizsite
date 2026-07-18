from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse

from .forms import EmailGateForm
from .models import AllowedEmail, Quiz, QuizAttempt, AnswerRecord

SESSION_EMAIL_KEY = "quiz_verified_email"


def email_gate(request):
    """Step 1: visitor enters their email. Only whitelisted emails proceed."""
    if request.method == "POST":
        form = EmailGateForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].strip().lower()
            try:
                allowed = AllowedEmail.objects.get(email__iexact=email)
            except AllowedEmail.DoesNotExist:
                messages.error(
                    request,
                    "This email is not authorized to take the quiz. "
                    "Please contact the administrator.",
                )
                return render(request, "quiz/email_gate.html", {"form": form})

            if allowed.has_attempted and not allow_retake_or_reset(allowed):
                messages.error(request, "You have already submitted this quiz.")
                return render(request, "quiz/email_gate.html", {"form": form})

            request.session[SESSION_EMAIL_KEY] = allowed.email
            return redirect("quiz:quiz_list")
    else:
        form = EmailGateForm()
    return render(request, "quiz/email_gate.html", {"form": form})


def allow_retake_or_reset(allowed_email: AllowedEmail) -> bool:
    """If retake is allowed, reset the attempted flag so the user can proceed."""
    if allowed_email.allow_retake:
        allowed_email.has_attempted = False
        allowed_email.allow_retake = False
        allowed_email.save(update_fields=["has_attempted", "allow_retake"])
        return True
    return False


def _get_verified_email(request):
    return request.session.get(SESSION_EMAIL_KEY)


def quiz_list(request):
    email = _get_verified_email(request)
    if not email:
        return redirect("quiz:email_gate")

    allowed = get_object_or_404(AllowedEmail, email__iexact=email)
    if allowed.has_attempted:
        messages.info(request, "You have already submitted a quiz.")
        return redirect("quiz:email_gate")

    quizzes = Quiz.objects.filter(is_active=True)
    return render(request, "quiz/quiz_list.html", {"quizzes": quizzes, "email": email})


def take_quiz(request, quiz_id):
    email = _get_verified_email(request)
    if not email:
        return redirect("quiz:email_gate")

    allowed = get_object_or_404(AllowedEmail, email__iexact=email)
    if allowed.has_attempted:
        messages.info(request, "You have already submitted this quiz.")
        return redirect("quiz:email_gate")

    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    questions = quiz.questions.all()

    if request.method == "POST":
        attempt = QuizAttempt.objects.create(
            email=allowed.email,
            quiz=quiz,
            total_marks=quiz.total_marks,
        )
        score = 0
        for question in questions:
            selected = request.POST.get(f"question_{question.id}", "")
            is_correct = selected == question.correct_option
            if is_correct:
                score += question.marks
            AnswerRecord.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected,
                is_correct=is_correct,
            )
        attempt.score = score
        attempt.submitted_at = timezone.now()
        attempt.save(update_fields=["score", "submitted_at"])

        allowed.has_attempted = True
        allowed.save(update_fields=["has_attempted"])

        request.session.pop(SESSION_EMAIL_KEY, None)

        return redirect(reverse("quiz:result", args=[attempt.id]))

    return render(
        request,
        "quiz/take_quiz.html",
        {"quiz": quiz, "questions": questions, "email": email},
    )


def result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    answers = attempt.answers.select_related("question").all()
    return render(
        request,
        "quiz/result.html",
        {"attempt": attempt, "answers": answers},
    )
