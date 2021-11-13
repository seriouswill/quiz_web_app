from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from quiz import my_questions
from questions import day_one_questions
from datetime import timedelta
import datetime

# graph imports
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.plotting import figure, show, gridplot
from bokeh.models import PrintfTickFormatter


app = Flask(__name__)
app.secret_key = "codenationquizapp"

# Database stuff
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days=7)


class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email


# global variables
ready = False
q_index = 0
score = 0
day_scores = [0, 0, 0, 0, 0, 0, 0]
days2 = [1, 2, 3, 4, 5, 6, 7]
wrong = 0
days_completed = 0
days = ["Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"]
day = 0
weekday = datetime.datetime.today().weekday()


@app.route('/')
def home():
    return render_template("index.html", score=0, q_index=0, wrong=0, days_completed=days_completed)

# view class results sections


@app.route('/view')
def view():
    return render_template("view.html", values=users.query.all())


@app.route('/daychoice')
def daychoice():
    return render_template("daychoice.html", days_completed=days_completed, days=days, weekday=weekday)


@app.route('/quiz/')
def quiz():
    global days_completed
    if "user" != session:
        flash(f"You should log in to store your results!")
    if days_completed > 5:
        days_completed = 0
    return render_template("quiz.html", day_one_questions=day_one_questions, q_index=0,
                           ready=False, day_scores=day_scores, wrong=0)


@app.route('/login/', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user
        session["days_completed"] = days_completed
        found_user = users.query.filter_by(name=user).first()
        if found_user:
            session["email"] = found_user.email
        else:
            usr = users(user, "")
            db.session.add(usr)
            db.session.commit()
        flash(f"You have been logged in sucessfully, {user}.", "info")
        return redirect(url_for("user", user=user))

    else:
        if "user" in session:
            flash(f"You are already logged in!")
            return redirect(url_for("user"))
        return render_template('login.html')


@app.route('/user', methods=["POST", "GET"])
def user():
    global days2, day_scores
    # create a new plot with a title and axis labels
    p = figure(title="Daily Scores",
               x_axis_label="Days", y_axis_label="Score")
    p.vbar(x=days2, top=day_scores, legend_label="Scores",
           width=0.5, bottom=0, color="red")
    # show(p)
    # trying to get monday to friday as ticks labels !!!!!
    # p.xaxis[0].formatter = PrintfTickFormatter(format="%s")
    script1, div1 = components(p)
    cdn_js = CDN.js_files[0]
    cdn_css = CDN.css_files
    email = None
    if "user" in session:
        user = session["user"]

        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = users.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit()
            flash(f"Your email, {email}, has been saved.")
        else:
            if email in session:
                email = session["email"]
        return render_template('userpage.html', user=user, email=email, days_completed=days_completed, days=days, day=day, day_scores=day_scores, script1=script1, div1=div1, cdn_js=cdn_js, cdn_css=cdn_css)
    else:
        return redirect(url_for("login"))


@app.route('/logout/')
def logout():
    global days_completed

    days_completed = 0
    if "user" in session:
        user = session["user"]
        flash(f"You have been logged out sucessfully, {user}.", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for('login'))


@app.route('/start/',  methods=["POST", "GET"])
def start():
    global ready
    ready = True
    db.session.commit()
    return render_template('/quiz.html', day_one_questions=day_one_questions, q_index=q_index,
                           ready=ready, day_scores=day_scores, days_completed=days_completed)


@app.route('/next/',  methods=["POST", "GET"])
def next():
    global q_index, score, wrong, days_completed, day, day_scores

    if request.method == 'POST':
        session.permanent = True
        choice = request.form.get("answer", type=str)
        if choice == day_one_questions[q_index]["correctAnswer"]:
            day_scores[days_completed] += 1
        else:
            wrong += 1

    if q_index < 9:
        q_index += 1
    else:
        q_index = 0
        #day_scores[days_completed] = score
        days_completed += 1
        day += 1

        if "user" in session:
            user = session["user"]
            return render_template('end.html', day_scores=day_scores, wrong=wrong, user=user, days_completed=days_completed)
        else:
            return render_template('end.html', day_scores=day_scores, wrong=wrong, days_completed=days_completed)
        # if my_questions[q_index]["answers"]["c"] == my_questions[0]["correctAnswer"]:
        #     print("Well done")

    return render_template('/quiz.html', day_one_questions=day_one_questions, q_index=q_index,
                           ready=ready, day_scores=day_scores, wrong=wrong, days_completed=days_completed)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
