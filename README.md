# Email-Gated Quiz Test (Django)

A Django project where only pre-approved emails can take a quiz. Questions are
defined together with their correct answer in the admin panel. When a
candidate submits, the app auto-grades the attempt against the stored answers
and shows a scored "question paper" style result (each question marked
correct/incorrect, with the right answer highlighted).

## Features

- **Email whitelist gate** (`AllowedEmail`) — only emails you add can access
  the quiz. No password/signup needed; they just type their email.
- **One attempt per email** — once submitted, the same email is blocked from
  retaking, unless you tick "Allow retake" in admin.
- **Questions + answers defined together** — each `Question` has options A–D
  and a `correct_option` field set right on the same record in admin.
- **Auto-grading on submit** — `take_quiz` view compares each submitted
  answer to `correct_option` and computes the score instantly.
- **Question-paper style result page** — shows every question, the
  candidate's answer, the correct answer, and a badge (Correct/Incorrect),
  plus the total score and percentage.
- **Countdown timer** — quiz auto-submits when the configured duration runs
  out.
- **Admin dashboard** — manage allowed emails, quizzes, questions, and view
  every attempt (with per-question breakdown) from `/admin/`.

## Project layout

```
quizsite/
├── manage.py
├── quizsite/            # project settings & urls
└── quiz/                 # the quiz app
    ├── models.py          # AllowedEmail, Quiz, Question, QuizAttempt, AnswerRecord
    ├── views.py           # email_gate, quiz_list, take_quiz, result
    ├── forms.py
    ├── admin.py
    ├── urls.py
    └── templates/quiz/    # email_gate, quiz_list, take_quiz, result
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install django

python manage.py migrate
python manage.py createsuperuser  # create an admin login
python manage.py runserver
```

Open http://127.0.0.1:8000/admin/ and log in with the superuser you created.

A demo superuser was created while building this project for testing:
- username: `admin`
- password: `admin12345`

**Change this password (or delete the user and create your own) before using
the project for anything real.**

## How to use it

1. In **/admin/**, open **Allowed emails** and add every email address that
   should be able to take the quiz (e.g. `student@example.com`).
2. Open **Quizzes** → **Add quiz**. Give it a title, description, duration
   (minutes), and add each **Question** inline: the question text, options
   A–D, pick the **correct option**, and set marks. Save.
3. Share the site's home URL (`/`) with the whitelisted candidates.
4. A candidate visits the site, types their email. If it's on the allowed
   list, they see the available quizzes, click **Start**, answer the
   questions, and click **Submit**.
5. On submit, the app grades it instantly and shows the score plus a full
   answer review (their answer vs. the correct answer for every question).
6. Their email is now marked "has attempted" so they can't retake it. You can
   tick **Allow retake** on their `AllowedEmail` record in admin if you want
   to let them try again.
7. See every submission and its score under **Quiz attempts** in admin
   (expand a row to see each question's recorded answer).

## Notes / things you may want to customize

- **No password/login for candidates** — access is only gated by knowing an
  allowed email, matching the "define emails who can see the question" ask.
  If you need stronger verification, add an emailed one-time code step in
  `email_gate` before setting the session.
- **Multiple choice only** — `correct_option` is a single choice (A–D). If
  you need short-answer/text questions with auto-grading, add a
  `question_type` field and compare submitted text (normalize + strip) to a
  stored expected answer.
- **Timer is client-side** — for exam-grade integrity, also enforce the
  duration server-side (store `started_at`, reject submissions after
  `started_at + duration_minutes`).
- **SECRET_KEY / DEBUG** — `quizsite/settings.py` still has the
  auto-generated dev `SECRET_KEY` and `DEBUG = True`. Change both, and set
  `ALLOWED_HOSTS` to your real domain, before deploying.
- **Database** — uses SQLite by default (`db.sqlite3`), fine for small
  deployments; swap to Postgres/MySQL for production scale.
