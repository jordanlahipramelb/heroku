from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Tweet
from forms import UserForm, TweetForm
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_demo"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "hellosecret1")
print("#########################################")
print(
    app.config["SECRET_KEY"]
)  # this should print hellosecret1 because we didn't set a secret key yet, but it's different on the heroku concole because we set that one
print("#########################################")
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False


connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route("/")
def home_page():
    return render_template("index.html")


@app.route("/tweets", methods=["GET", "POST"])
def show_tweets():

    # if a user_id isn't stored in the session, that means there is no user logged in
    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect("/")

    form = TweetForm()
    # in the future, more efficient to send a single query using a join so you don't have to type a ton of queries (refer to WTForms and JOINS: FirstFlaskApp-PythonSQLFlask/ )
    # EX: add a column to tweets table
    #   number of likes, avatar photo, date created
    all_tweets = Tweet.query.all()

    if form.validate_on_submit():
        text = form.text.data
        # user should be logged in when creating a tweet, so the session should have the id
        new_tweet = Tweet(text=text, user_id=session["user_id"])
        db.session.add(new_tweet)
        db.session.commit()
        flash("Tweet Created!", "success")
        return redirect("/tweets")

    return render_template("tweets.html", form=form, tweets=all_tweets)


@app.route("/tweets/<int:id>", methods=["POST"])
def delete_tweet(id):
    """Delete tweet."""

    # this will add protection so a different user/unregistered won't be able to access someones tweet
    if "user_id" not in session:
        flash("Please login first", "danger")
        return redirect("/login")
    tweet = Tweet.query.get_or_404(id)

    # if the person who is logged in is the owner of that tweet, they will have access to delete their own tweet
    if tweet.user_id == session["user_id"]:
        db.session.delete(tweet)
        db.session.commit()
        flash("Tweet deleted.", "info")
        return redirect("/tweets")

    flash("You don't have permission to that tweet.", "danger")
    return redirect("/tweets")


# route submits to same URL, but will redirect through conditions
@app.route("/register", methods=["GET", "POST"])
def register_user():

    # may want separate Form for registration
    form = UserForm()
    if form.validate_on_submit():
        # retrieve data from inputs on form
        username = form.username.data
        password = form.password.data

        # classmethod instance
        new_user = User.register(username, password)
        db.session.add(new_user)

        # tries to commit, but if there is an Integrity Error, it will run except
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username taken. Please pick another.")
            return render_template("register.html", form=form)

        # adds the user.id to the session so the browser remembers that they are logged in
        session["user_id"] = new_user.id  # keep logged in

        flash("Welcome! Successfully created your account.", "success")
        return redirect("/tweets")

    return render_template("register.html", form=form)


# route submits to same URL, but will redirect through conditions
@app.route("/login", methods=["GET", "POST"])
def login_user():

    form = UserForm()

    if form.validate_on_submit():
        # retrieve data from inputs on form
        username = form.username.data
        password = form.password.data

        # tries to find the user with that username; you are who you say you are
        #   authenticate will use bcrypt to check (boolean) if password and hashed pwd are the same
        user = User.authenticate(username, password)

        # if the user is found, redirect to tweets page
        if user:
            flash(f"Welcome back {user.username}!", "primary")

            # adds the user.id to the session so the browser remembers that they are logged in
            session["user_id"] = user.id  # keep logged in
            return redirect("/tweets")

        # False/invalid credentials: return error message in HTML
        else:
            # this targets the form -> username label/input error section
            form.username.errors = ["Invalid username/password."]

    return render_template("login.html", form=form)


# logging out should be a POST request because there are side effects, but most browsers utilize prefetching (send a request to that URL) and if it's a GET request, it will just log you out.
# it is standard to use a POST route
@app.route("/logout", methods=["POST"])
def logout_user():

    session.pop("user_id")
    flash("Goodbye!", "info")
    return redirect("/")
