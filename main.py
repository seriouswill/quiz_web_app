
# FLASK IMPORTS
from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy

# FORMS IMPORTS
from flask_wtf import FlaskForm
from sqlalchemy.orm import backref
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_manager, login_user, login_required, logout_user, current_user

# DATETIME IMPORTS
from datetime import timedelta
import datetime

# LOCAL IMPORTS
from questions import day_one_questions, day_two_questions

# GREAPH IMPORTS
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.plotting import figure, show, gridplot
from bokeh.models import PrintfTickFormatter


app = Flask(__name__)
app.secret_key = "codenationquizapp"
bootstrap = Bootstrap(app)


# Database stuff

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days=7)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    image_file = db.Column(
        db.String(20), default='./static/images.default.jpg')
    user_days_completed = db.Column(db.Integer, default=0)
    score = db.relationship('Score', backref='username', lazy=True)

    def __repr__(self):
        return f"{self.username} = username, {self.email} = email, {self.password} = password"


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monday_score = db.Column(db.Integer, default=0)
    tuesday_score = db.Column(db.Integer, default=0)
    wednesday_score = db.Column(db.Integer, default=0)
    thursday_score = db.Column(db.Integer, default=0)
    friday_score = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Score:  {self.monday_score} Tuesday: {self.tuesday_score}."


@ login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# global variables
ready = False
q_index = 0
score = 0
day_scores = [0, 0, 0, 0, 0]
user_daily_scores = [Score.monday_score, ]
days2 = [1, 2, 3, 4, 5]
wrong = 0
days_completed = 0
days = ["Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"]
day = 0
weekday = datetime.datetime.today().weekday()


# ~~~~~~~~~~~~~~~~~ SIGN UP SECTION


class LoginForm(FlaskForm):
    username = StringField('username',
                           validators=[InputRequired(), Length(min=4, max=17)])
    password = PasswordField('password',
                             validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


class RegisterForm(FlaskForm):
    username = StringField('username',
                           validators=[InputRequired(), Length(min=4, max=17)])
    password = PasswordField('password',
                             validators=[InputRequired(), Length(min=8, max=80)])
    email = StringField('email', validators=[InputRequired(), Email(
        message="Invalid Email"), Length(max=50)])


@ app.route('/signup/', methods=["GET", "POST"])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method="sha256")
        new_user = User(username=form.username.data,
                        email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('user'))
        # return '<h1>' + form.username.data + form.password.data + '</h1>'

    return render_template('signup.html', form=form)


@app.route('/login/', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('user'))
        return '<h1> Invalid Username or Password </h1>'
        # return '<h1>' + form.username.data + form.password.data + '</h1>'

    return render_template('login.html', form=form)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ~~~~~~~~~~~~~~~~~~~~~ ROUTES SECTION


@app.route('/')
def home():
    return render_template("index.html", score=0, q_index=0, wrong=0, days_completed=current_user.user_days_completed)


@app.route('/user', methods=["POST", "GET"])
@login_required
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
    # if "user" in session:
    #     user = session["user"]

    #     if request.method == "POST":
    #         email = request.form["email"]
    #         session["email"] = email
    #         found_user = users.query.filter_by(name=user).first()
    #         found_user.email = email
    #         db.session.commit()
    #         flash(f"Your email, {email}, has been saved.")
    #     else:
    #         if email in session:
    #             email = session["email"]
    return render_template('userpage.html', user=user, name=current_user.username, email=email, days_completed=days_completed, days=days,
                           day=day, day_scores=day_scores, script1=script1, div1=div1, cdn_js=cdn_js, cdn_css=cdn_css)
    # else:
    #     return redirect(url_for("login"))
# view class results sections


@app.route('/view')
def view():
    return render_template("view.html", values=User.query.all())


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
    return render_template("quiz.html", day_one_questions=day_one_questions, day_two_questions=day_two_questions, q_index=0,
                           ready=False, day_scores=day_scores, wrong=0)


# @login required - this is throwing an error, might need to rename login to login
@app.route('/start/',  methods=["POST", "GET"])
def start():
    global ready
    ready = True
    db.session.commit()
    return render_template('/quiz.html', day_one_questions=day_one_questions, q_index=q_index,
                           ready=ready, day_scores=day_scores, days_completed=days_completed, day_two_questions=day_two_questions)


@app.route('/next/',  methods=["POST", "GET"])
def next():
    global q_index, score, wrong, days_completed, day, day_scores

    if request.method == 'POST':
        session.permanent = True
        choice = request.form.get("answer", type=str)
        if days_completed == 0:
            if choice == day_one_questions[q_index]["correctAnswer"]:
                day_scores[days_completed] += 1
            else:
                wrong += 1
            new_score = Score(monday_score=day_scores[days_completed])
            db.session.add(new_score)
        elif days_completed == 1:
            if choice == day_two_questions[q_index]["correctAnswer"]:
                day_scores[days_completed] += 1
            else:
                wrong += 1
            new_score = Score(tuesday_score=day_scores[days_completed])
            db.session.add(new_score)
        db.session.commit()
    if q_index < 9:
        q_index += 1
    else:
        q_index = 0
        # day_scores[days_completed] = score
        days_completed += 1
        try:
            new_user_daily_score = User(user_days_completed=days_completed)
            db.session.add(new_user_daily_score)
            db.session.commit()

        except:
            print("There has been an error updating user_days_completed")

        day += 1

        return render_template('end.html', day_scores=day_scores, wrong=wrong, user=current_user.username, days_completed=days_completed)

        # if my_questions[q_index]["answers"]["c"] == my_questions[0]["correctAnswer"]:
        #     print("Well done")

    return render_template('/quiz.html', day_one_questions=day_one_questions, day_two_questions=day_two_questions, q_index=q_index,
                           ready=ready, day_scores=day_scores, wrong=wrong, days_completed=days_completed)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
