
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
