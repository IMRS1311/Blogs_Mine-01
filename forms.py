from flask import Flask
from wtforms import StringField, SubmitField, EmailField, IntegerField, PasswordField, URLField, SelectField, SearchField, FileField
from wtforms.validators import InputRequired, Length, Email, EqualTo, URL, Regexp
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditor, CKEditorField
from database import BlogPosts
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
ckeditor = CKEditor(app)

# ---------------------------------- CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///blogs-database.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=3, max=50, message="Length must be between 3 and 50 Characters")])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    phone = IntegerField('Phone', validators=[InputRequired()])
    message = StringField('Message', validators=[InputRequired(), Length(min=10, max=500, message="Length must be between 10 and 500 Characters")])
    submit = SubmitField(label="Submit")


class SignupForm(FlaskForm):
        name = StringField('Name', validators=[InputRequired(), Length(min=3, max=50, message="Length must be between 3 and 50 Characters")])
        email = EmailField('Email', validators=[InputRequired(), Email()])
        password = PasswordField('Password', validators=[InputRequired(), EqualTo('confirm', message='Passwords must match'), Length(min=6, max=50, message="Length must be between 6 and 50 Characters")])
        confirm = PasswordField('Repeat Password')
        profile_photo = FileField('Your Profile Photo')
        submit = SubmitField(label="Sign Up")


class LoginForm(FlaskForm):
        email = EmailField('Email', validators=[InputRequired(), Email()])
        password = PasswordField('Password', validators=[InputRequired()])
        submit = SubmitField(label="Log In")


class SelectForm(FlaskForm):
    with app.app_context():
        blogs = db.session.query(BlogPosts).all()
        titles = [blog.title for blog in blogs]
        select = SelectField("Select By Title", choices=titles)


class SearchForm(FlaskForm):
        search = SearchField("Search Posts")


class BlogsForm(FlaskForm):
    title = StringField('Post Title', validators=[InputRequired()])
    subtitle = StringField('Post Subtitle', validators=[InputRequired()])
    body = CKEditorField('Post Details', validators=[InputRequired()])
    image = URLField('Image', validators=[URL()])
    submit = SubmitField(label="Submit")


class CommentsForm(FlaskForm):
    comment_text = CKEditorField('Comment', validators=[InputRequired()])
    submit = SubmitField(label="Submit")



