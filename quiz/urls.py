from django.urls import path
from . import views

app_name = "quiz"

urlpatterns = [
    path("", views.email_gate, name="email_gate"),
    path("quizzes/", views.quiz_list, name="quiz_list"),
    path("quiz/<int:quiz_id>/", views.take_quiz, name="take_quiz"),
    path("result/<int:attempt_id>/", views.result, name="result"),
]
