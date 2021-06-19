from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


# give ownership to tweets
class Tweet(db.Model):

    __tablename__ = "tweets"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    text = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # connects User and Tweet models
    user = db.relationship("User", backref="tweets")

    # EX
    # tweet.user.username // displays username


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    # start_register
    # it's good to move logic out of view functions from app.py because it is dealing with the User model
    # ran in the User model EX: User.register, User.authentication
    # generates new instance of that cls
    @classmethod
    def register(cls, username, pwd):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)

        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        #   important to pass in hashed for password, not actual pwd
        return cls(username=username, password=hashed_utf8)

    # In [3]: u = User.register('mrmonkey1', 'bananaslol')
    # In [5]: u.password
    # Out[5]: '$2b$12$zoAWa2378MHD5rFJ/6.Y3.qMHzgjM1Thqom8RVJmNc/tu0BjjeTte'

    # save user to DB
    # In [7]: db.session.add(u)
    # In [8]: db.session.commit()

    # end_register

    # start_authenticate
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        # searches for the user
        user = User.query.filter_by(username=username).first()
        # uses .first becuse there should be 0 or only 1 with that username
        # cant authenticate if we cant find the username

        # user.password is hashed password. That hashed password should be the pwd entered pre hashed
        if user and bcrypt.check_password_hash(user.password, pwd):
            # return user instance
            return user
        else:
            return False

    # EXAMPLE
    # In [11]: User.authenticate('mrmonkey1', '1234')
    # Out[11]: False

    # In [12]: User.authenticate('mrmonkey1', 'bananaslol')
    # Out[12]: <User 1>

    # end_authenticate