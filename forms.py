from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired


class UserForm(FlaskForm):

    # input_name = TypeField("Label_name", validators=[ValidatorName()])

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class TweetForm(FlaskForm):

    text = TextAreaField("Tweet Text", validators=[InputRequired()])
