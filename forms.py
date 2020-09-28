from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired

# Note that we'll only have one form here just to keep things simple.
# Often, the login and registration forms are separate.
# This is helpful if you want to capture other informaiton when a user registers (e.g., first and last name, security question, and whatever else--maybe birthday or address or whatever...)
# And then the login form is just username and password.


class UserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


# For tweets, we will also capture user id, but that will come from the session for the currently logged in user.
class TweetForm(FlaskForm):
    text = StringField("Tweet Text", validators=[InputRequired()])
