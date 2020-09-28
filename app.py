"""Example flask app that stores passwords hashed with Bcrypt. Yay!"""

from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Tweet
from forms import UserForm, TweetForm
# RegisterForm, LoginForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///auth_demo"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
# db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route("/")
def home_page():
    """Show homepage."""

    return render_template("index.html")


@app.route("/tweets", methods=['GET', 'POST'])
def show_tweets():
    """"""

    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect('/')

    # The code below will only run if there is a logged in user.

    # We could put this form instance above the if stmt, and it wouldn't affect what the user sees, but there's no sense in creating an instance of the form if we are just going to redirect anyway.
    form = TweetForm()

    all_tweets = Tweet.query.all()

    if form.validate_on_submit():
        text = form.text.data
        new_tweet = Tweet(text=text, user_id=session["user_id"])

        db.session.add(new_tweet)
        db.session.commit()
        flash("Tweet Created!", "success")
        return redirect('/tweets')

    return render_template("tweets.html", form=form, tweets=all_tweets)

# We are NOT following RESTful routing conventions here (unfortunately)


@app.route('/tweets/<int:id>', methods=["POST"])
def delete_tweet(id):
    """Delete tweet:
    Find the tweet with the given id.
    Verify the the current logged in user is the owner of the tweet. """

    # In Python, if a key in a dictionary is not found, we'll get a Key Error.
    # So, let's add in protection.
    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')

    tweet = Tweet.query.get_or_404(id)

    # Logged in user owns the tweet
    if tweet.user_id == session['user_id']:
        db.session.delete(tweet)
        db.session.commit()
        flash("Tweet deleted!", "info")
        return redirect('/tweets')

    # Logged in user does NOT own the tweet
    flash("You don't have permission to do that!", "danger")
    return redirect('/tweets')

    # We should also be making sure that a user who is not logged in cannot delete any tweets and give them a different message (e.g., "Please log in first.").  Right now, they would see the message above about not having permission to do that.


@app.route("/register", methods=["GET", "POST"])
def register_user():
    """Register user: produce form & handle form submission."""

    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data

        # there is at least one scenario where this would fail: the username is already taken
        # you should handle this error, but we won't do it here
        # so, consider re-rendering the form showing the error
        new_user = User.register(username, pwd)

        db.session.add(new_user)
        db.session.commit()
        session["user_id"] = new_user.id

        flash('Welcome! Successfully Created Your Account!', "success")

    #     # on successful login, redirect to secret page
        # return redirect("/secret")
        return redirect("/tweets")

    # else:
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_user():
    """Produce login form or handle login."""

    # form = LoginForm()
    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # authenticate will return the user object found in the table or False
        user = User.authenticate(username, password)

        if user:
            flash(f'Welcome back, { user.username }', 'primary')
            session["user_id"] = user.id  # keep logged in
            # return redirect("/secret")
            return redirect('/tweets')

        else:
            form.username.errors = ["Invalid username/password"]

    return render_template("login.html", form=form)
# end-login


# @app.route("/secret")
# def secret():
#     """Example hidden page for logged-in users only."""

#     if "user_id" not in session:
#         flash("You must be logged in to view!")
#         return redirect("/")

#         # alternatively, can return HTTP Unauthorized status:
#         #
#         # from werkzeug.exceptions import Unauthorized
#         # raise Unauthorized()

#     else:
#         return render_template("secret.html")


# Make logout a POST route!
@app.route("/logout")
def logout_user():
    """Logs user out and redirects to homepage."""

    session.pop("user_id")

    flash("Goodbye!", "info")
    return redirect("/")
