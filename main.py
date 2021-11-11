from flask import Flask, redirect, url_for, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_navigation import Navigation
from quiz import my_questions
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "codenationquizapp"
app.permanent_session_lifetime = timedelta(days=7)

nav = Navigation(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

#global variables
ready = False
q_index = 0
score = 0
wrong = 0
days_completed = 0

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
day = 0


@app.route('/')
def home():
    return render_template("index.html", score=0, q_index=0, wrong=0, days_completed=days_completed)


@app.route('/quiz/')
def quiz():
    return render_template("quiz.html", my_questions=my_questions, q_index=0,
                           ready=False, score=0, wrong=0)


@app.route('/login/', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user
        session["days_completed"] = days_completed
        return redirect(url_for("user", user=user))
    else:
        if "user" in session:
            return redirect(url_for("user"))
        return render_template('login.html')


@app.route('/user')
def user():
    if "user" in session:
        user = session["user"]
        return render_template('userpage.html', user=user, days_completed=days_completed, days=days, day=day, score=score)

    else:
        return redirect(url_for("login"))


@app.route('/logout/')
def logout():
    global days_completed
    session.pop("user", None)
    days_completed = 0
    return redirect(url_for('login'))


@app.route('/start/',  methods=["POST", "GET"])
def start():
    global ready
    ready = True
    db.session.commit()
    return render_template('/quiz.html', my_questions=my_questions, q_index=q_index,
                           ready=ready, score=score)


@app.route('/next/',  methods=["POST", "GET"])
def next():
    global q_index, score, wrong, days_completed, day

    if request.method == 'POST':
        session.permanent = True
        choice = request.form.get("answer", type=str)

        if choice == my_questions[q_index-1]["correctAnswer"]:
            print(choice)
            score += 1
            print(score)
        else:
            print("Thes else is executing")
            print(choice)
            print(my_questions[q_index-1]["correctAnswer"])
            wrong += 1
            print(score, wrong)
    if q_index < 2:
        q_index += 1
    else:
        q_index = 0
        days_completed += 1
        day += 1
        if "user" in session:
            user = session["user"]
            return render_template('end.html', score=score, wrong=wrong, user=user)
        # if my_questions[q_index]["answers"]["c"] == my_questions[0]["correctAnswer"]:
        #     print("Well done")

    return render_template('/quiz.html', my_questions=my_questions, q_index=q_index,
                           ready=ready, score=score, wrong=wrong)


if __name__ == '__main__':
    app.run(debug=True)
