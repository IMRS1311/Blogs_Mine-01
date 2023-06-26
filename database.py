from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import UserMixin
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, declarative_base


app = Flask(__name__)

db = SQLAlchemy()
Base = declarative_base()

# ---------------------------------- CREATE DATABASE
app.config['SECRET_KEY'] = "c39b2dfd4311f41cdd79730f59efa3c94f2a538dd65773533181fbf418a081a4"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///blogs-database.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ------------------------------------ CREATE TABLES
with app.app_context():

    # -------- Users Table
    class Users(UserMixin, db.Model, Base):
        __tablename__ = "users"
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(100), unique=True, nullable=False)
        password = db.Column(db.String(50), nullable=False)
        profile_photo = db.Column(db.String(500), nullable=True)
        signup_date = db.Column(db.String(20), nullable=False)
        signup_time = db.Column(db.String(20), nullable=False)
        posts = relationship("BlogPosts", back_populates="post_author")
        comments = relationship("Comments", back_populates="comment_author")
        replies = relationship("Replies", back_populates="reply_author")
        logins = relationship("LoginData", back_populates="user")
        logouts = relationship("LogoutData", back_populates="user")


        # Optional: this will allow each book object to be identified by its title when printed.
        # def __repr__(self):
        #     return f'<Users{self.email}>'


    db.create_all()

    # new_user = Users(name="Eslam",
    #                      email="imrs1311@gmail.com",
    #                      password="Thanks",
    #                      signup_date="May 28, 2023",
    #                      signup_time="16:23:45"
    #                      )
    # db.session.add(new_user)
    # db.session.commit()

    # -------- Blogs Table
    class BlogPosts(db.Model, Base):
        __tablename__ = "blog_posts"
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(50), nullable=False)
        subtitle = db.Column(db.String(100), nullable=False)
        body = db.Column(db.Text, nullable=False)
        blog_date = db.Column(db.String(20), nullable=False)
        blog_time = db.Column(db.String(20), nullable=False)
        image_url = db.Column(db.String(500), nullable=False)
        author_id = db.Column(Integer, ForeignKey('users.id'))
        post_author = relationship("Users", back_populates="posts")
        comments = relationship("Comments", back_populates="parent_post")

        # Optional: this will allow each book object to be identified by its title when printed.
        def __repr__(self):
            return f'<Blogs {self.title}>'

    db.create_all()
    #
    # new_blog = Blogs(title="The Life of Cactus",
    #                  subtitle="Who knew that cacti lived such interesting lives.",
    #                  body="Nori grape silver beet broccoli kombu beet greens fava bean potato quandong celery. Bunya nuts black-eyed pea prairie turnip leek lentil turnip greens parsnip. Sea lettuce lettuce water chestnut eggplant winter purslane fennel azuki bean earthnut pea sierra leone bologi leek soko chicory celtuce parsley j\u00edcama salsify.",
    #                  author="E. M. Rashed",
    #                  email = "imrs1311@gmail.com",
    #                  blog_date="May 28, 2023",
    #                  blog_time="16:23:45",
    #                  image_url="/static/assets/img/image1.jpg"
    #                  )
    # db.session.add(new_blog)
    # db.session.commit()

    # -------- Comments Table
    class Comments(db.Model, Base):
        __tablename__ = "comments"
        id = db.Column(db.Integer, primary_key=True)
        comment_text = db.Column(db.Text, nullable=False)
        post_id = db.Column(Integer, ForeignKey('blog_posts.id'))
        parent_post = relationship("BlogPosts", back_populates="comments")
        author_id = db.Column(Integer, ForeignKey('users.id'))
        comment_author = relationship("Users", back_populates="comments")
        replies = relationship("Replies", back_populates="parent_comment")

        # Optional: this will allow each book object to be identified by its title when printed.
        def __repr__(self):
            return f'<Blogs {self.comment_text}>'

    db.create_all()

    # -------- Reply Table
    class Replies(db.Model, Base):
        __tablename__ = "replies"
        id = db.Column(db.Integer, primary_key=True)
        reply_text = db.Column(db.Text, nullable=False)
        comment_id = db.Column(Integer, ForeignKey('comments.id'))
        parent_comment = relationship("Comments", back_populates="replies")
        author_id = db.Column(Integer, ForeignKey('users.id'))
        reply_author = relationship("Users", back_populates="replies")

        # Optional: this will allow each book object to be identified by its title when printed.
        def __repr__(self):
            return f'<Blogs {self.reply_text}>'

    db.create_all()

    # -------- Contacts Table
    class Contacts(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(100), nullable=False)
        phone = db.Column(db.Integer, nullable=False)
        message = db.Column(db.String(500), nullable=False)
        msg_date = db.Column(db.String(20), nullable=False)
        msg_time = db.Column(db.String(20), nullable=False)

        # Optional: this will allow each book object to be identified by its title when printed.
        # def __repr__(self):
        #     return f'<Contacts {self.email}>'

    db.create_all()
    #
    # new_contact = Contacts(name="Eslam",
    #                        email="imrs1311@gmail.com",
    #                        phone="0521067175",
    #                        message="Thanks",
    #                        msg_date="May 28, 2023",
    #                        msg_time="16:23:45"
    #                        )
    # db.session.add(new_contact)
    # db.session.commit()

    # -------- Login Table
    class LoginData(db.Model, Base):
        __tablename__ = "logindata"
        id = db.Column(db.Integer, primary_key=True)
        login_date = db.Column(db.String(20), nullable=False)
        login_time = db.Column(db.String(20), nullable=False)
        user = relationship("Users", back_populates="logins")
        user_id = db.Column(Integer, ForeignKey('users.id'))
        # Optional: this will allow each book object to be identified by its title when printed.
        # def __repr__(self):
        #     return f'<LoginData {self.email}>'

    db.create_all()
    #
    # new_login = LoginData(name="Eslam",
    #                       email="imrs1311@gmail.com",
    #                       password="Thanks",
    #                       login_date="May 28, 2023",
    #                       login_time="16:23:45"
    #                       )
    #
    # db.session.add(new_login)
    # db.session.commit()

    # -------- Logout Table
    class LogoutData(db.Model, Base):
        __tablename__ = "logoutdata"
        id = db.Column(db.Integer, primary_key=True)
        logout_date = db.Column(db.String(20), nullable=False)
        logout_time = db.Column(db.String(20), nullable=False)
        user = relationship("Users", back_populates="logouts")
        user_id = db.Column(Integer, ForeignKey('users.id'))
        # Optional: this will allow each book object to be identified by its title when printed.
        # def __repr__(self):
        #     return f'<LogoutData {self.email}>'

    db.create_all()
    #
    # new_logout = LogoutData(name="Eslam",
    #                         email="imrs1311@gmail.com",
    #                         logout_date="May 28, 2023",
    #                         logout_time="16:23:45"
    #                         )
    #
    # db.session.add(new_logout)
    # db.session.commit()



