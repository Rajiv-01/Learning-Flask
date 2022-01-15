
from unicodedata import east_asian_width
from flask import Flask, redirect, session, url_for, render_template, request, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "super secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)


class User(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100))
    phone = db.Column("phone", db.Integer)

    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = phone


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user_name = request.form["nm"]
        user_mail = request.form["mail"]
        session["user"] = user_name
        session["email"] = user_mail

        found_user = User.query.filter_by(name=user_name).first()
        if found_user:
            session["phone"] = found_user.phone

        else:
            usr = User(user_name, user_mail, None)
            db.session.add(usr)
            db.session.commit()
        return redirect(url_for("user"))
    else:
        if "user" in session:
            return redirect(url_for("user"))
        return render_template("login.html")


@app.route('/logout')
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"You have been logged out! {user}", 'info')
    session.pop("user", None)
    session.pop("email", None)
    session.pop("phone", None)

    return redirect(url_for("login"))


@app.route("/view")
def view():
    return render_template("view.html", values=User.query.all())


@app.route("/user", methods=["POST", "GET"])
def user():
    number = None
    if 'user' in session:
        user = session["user"]
        email = session["email"]
        if request.method == "POST":
            number = request.form["phone"]
            session["phone"] = number
            found_user = User.query.filter_by(name=user).first()
            found_user.phone = number
            db.session.commit()

        else:
            if "phone" in session:
                number = session["phone"]
        return render_template('user.html', name=user, email=email, phone=number)
    return redirect(url_for("login"))


@app.route("/delete/<int:id>")
def delete(id):
    found_user = User.query.filter_by(_id=id)
    flash(f"{found_user.first().name} has been removed")
    if found_user:
        if (found_user.first().name == session["user"] and found_user.first().email == session["email"]):
            session.pop("user")
            session.pop("email")
            session.pop("phone")
        found_user.delete()
        db.session.commit()

    return redirect(url_for("view"))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
