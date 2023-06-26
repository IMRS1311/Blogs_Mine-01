from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import smtplib
from database import BlogPosts, Contacts, LoginData, LogoutData, Users, Comments, Replies, db
from forms import ContactForm, SignupForm, LoginForm, SelectForm, SearchForm, BlogsForm, CommentsForm
import os

app = Flask(__name__)
ckeditor = CKEditor(app)
global logged_in, username, num
num = ""
gravatar = Gravatar(app, size=25, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)


# ---------------------------------- CREATE DATABASE
app.config['SECRET_KEY'] = "1234567890"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///blogs-database.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'
Bootstrap(app)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


my_email = os.environ.get("my_email")
my_password = os.environ.get("my_password")


with app.app_context():
    posts = db.session.query(BlogPosts).all()


    @app.route('/')
    def home():
        # if not current_user:
        post_id = int(request.args.get('post_id', 0))
        is_delete = request.args.get('is_delete')
        posts = db.session.query(BlogPosts).all()
        return render_template('index.html', posts=posts, post_id=int(post_id), is_delete=is_delete, logged_in=current_user.is_authenticated)
        # else:
        #     return redirect(url_for('select_page', logged_in=current_user.is_authenticated, sent_msg=False))


    @app.route('/about')
    def about_page():
        return render_template('about.html', logged_in=current_user.is_authenticated)


    # -------------------------------- Sign Up ----------------------------- #
    @app.route('/signup', methods=['POST', 'GET'])
    def signup_page():
        if current_user.is_authenticated:
            return redirect(url_for('select_page', logged_in=current_user.is_authenticated))
        else:
            sform = SignupForm()
            if sform.validate_on_submit():
                if Users.query.filter_by(email=sform.email.data).first():
                    flash("You've already signed up with that email, log in instead!")
                    return redirect(url_for('login_page', logged_in=current_user.is_authenticated))
                else:
                    photo = sform.profile_photo.data
                    if photo:
                        filename = secure_filename(photo.filename)
                        save_path = os.path.join('static', 'assets', 'img', filename)
                        photo.save(os.path.join(app.root_path, save_path))
                        profile_photo = '/' + save_path.replace(os.sep, '/')
                    else:
                        profile_photo = ""
                    new_user = Users(name=sform.name.data,
                                     email=sform.email.data,
                                     password=generate_password_hash(sform.password.data, method='pbkdf2:sha256', salt_length=8),
                                     profile_photo=profile_photo,
                                     signup_date=datetime.now().strftime("%a  %d/%m/%y"),
                                     signup_time=datetime.now().strftime("%H:%M:%S")
                                     )
                    db.session.add(new_user)
                    db.session.commit()
                    login_user(new_user)

                    new_login = LoginData(user=new_user,
                                          login_date=datetime.now().strftime("%a  %d/%m/%y"),
                                          login_time=datetime.now().strftime("%H:%M:%S")
                                          )
                    db.session.add(new_login)
                    db.session.commit()

                    # Log in and authenticate user after adding details to database.

                    message = f"Congrats.\nYou have signed up successfully in our blog on {new_user.signup_date} at {new_user.signup_time}."
                    send_email_signup(message, new_user.name, new_user.email)
                    return redirect(url_for("select_page", name=current_user.name, logged_in=current_user.is_authenticated, message="signed up", sent_msg=True))

            return render_template('signup.html', form=sform)


    def send_email_signup(message, name, email):
        email_message = f"Subject:New Sign-up to MyBlog  \n\n{message}\nYour name: {name}\nEmail: {email}\n"
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(my_email, my_password)
            connection.sendmail(my_email, email, email_message)

    # -------------------------------- Log In ----------------------------- #
    @app.route('/login', methods=['POST', 'GET'])
    def login_page():
        if current_user.is_authenticated:
            return redirect(url_for('select_page', name=current_user.name, logged_in=current_user.is_authenticated))
        else:
            lform = LoginForm()
            if lform.validate_on_submit() and request.method == 'POST':
                email = lform.email.data
                user = Users.query.filter_by(email=email).first()
                if not user:
                    flash('Incorrect email, please try again.')
                    return redirect(url_for('login_page'))

                # Check stored password hash against entered password hashed.
                elif not check_password_hash(user.password, lform.password.data):
                    flash('Incorrect password, please try again.')
                    return redirect(url_for('login_page'))

                login_user(user)
                new_login = LoginData(user=user,
                                      login_date=datetime.now().strftime("%a  %d/%m/%y"),
                                      login_time=datetime.now().strftime("%H:%M:%S")
                                      )
                db.session.add(new_login)
                db.session.commit()
                print(new_login.user.name)
                print(new_login.login_date)
                print(new_login.login_time)
                message = f"Welcome {new_login.user.name},\nYou have logged in our blog on {new_login.login_date} at {new_login.login_time}."
                send_email_login(message, new_login.user.name, new_login.user.email)
                lform = LoginForm(formdata=None)
                return redirect(url_for('select_page', lform=lform, name=current_user.name, logged_in=current_user.is_authenticated, message="logged in", sent_msg=True))

            return render_template('login.html', lform=lform)


    def send_email_login(message, name, email):
        email_message = f"Subject:New Log-in to MyBlog  \n\n{message}\nYour name: {name}\nEmail: {email}\n"
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(my_email, my_password)
            connection.sendmail(my_email, email, email_message)

    # -------------------------------- logout ---------------------------------- #
    @app.route('/logout', methods=['POST', 'GET'])
    def logout():
        if current_user:
            new_logout = LogoutData(user=current_user,
                                    logout_date=datetime.now().strftime("%a  %d/%m/%y"),
                                    logout_time=datetime.now().strftime("%H:%M:%S")
                                    )

            db.session.add(new_logout)
            db.session.commit()
        logout_user()
        return redirect(url_for('home', logged_in=current_user.is_authenticated))

    # ---------------------------------  Selection -------------------------------------- #
    @app.route('/select', methods=['POST', 'GET'])
    @login_required
    def select_page():
        xform = SelectForm()
        hform = SearchForm()
        sent_msg = request.args.get('sent_msg')
        message = request.args.get('message')

        if request.method == "POST":
            if xform.validate_on_submit():
                title = xform.select.data
                posts = db.session.query(BlogPosts).all()
                if posts:
                    print(posts)
                    for post in posts:
                        if post.title == title:
                            num = post.id
                            return redirect(url_for('post_page', num=num, name=current_user.name, logged_in=current_user.is_authenticated))
                else:
                    flash('No posts to view.')
            elif hform.validate_on_submit():
                text = hform.search.data
                fetched_posts = []
                posts = db.session.query(BlogPosts).all()
                if posts:
                    for post in posts:
                        if str(text) in post.title or str(text) in post.subtitle or str(text) in post.body:
                            fetched_posts.append(post)
                else:
                    flash('No posts to view!')
                if fetched_posts:
                    xform = SelectForm(formdata=None)
                    return render_template('select.html', xform=xform, hform=hform, name=current_user.name, logged_in=current_user.is_authenticated, posts=fetched_posts, results=True)

        return render_template('select.html', xform=xform, hform=hform, name=current_user.name, logged_in=current_user.is_authenticated, message=message, sent_msg=sent_msg)

    # ---------------------------------  PosT Input -------------------------------------- #
    @app.route('/blogging', methods=['POST', 'GET'])
    @login_required
    def blogging_page():
        bform = BlogsForm()
        if bform.validate_on_submit() and request.method == "POST":
            new_blog = BlogPosts(title=bform.title.data,
                                 subtitle=bform.subtitle.data,
                                 body=bform.body.data.replace('<p>', '').replace('</p>', ''),
                                 post_author=current_user,
                                 blog_date=datetime.now().strftime("%b %d, %y"),
                                 blog_time=datetime.now().strftime("%H:%M:%S"),
                                 image_url=bform.image.data
                                 )
            db.session.add(new_blog)
            db.session.commit()

            return redirect(url_for('home', name=current_user.name, logged_in=current_user.is_authenticated))

        return render_template('blogging.html', bform=bform, name=current_user.name, logged_in=current_user.is_authenticated)

    # ---------------------------------  Edit PosT  -------------------------------------- #
    @app.route('/edit_post', methods=['POST', 'GET'])
    @login_required
    def edit_page():
        post_id = request.args.get('post_id')
        post = db.session.get(BlogPosts, post_id)
        if not post:
            return redirect(url_for('login_page', logged_in=current_user.is_authenticated))
        elif current_user.is_authenticated and current_user == post.post_author:
            eform = BlogsForm(title=post.title, subtitle=post.subtitle, body=post.body, image=post.image_url)
            if eform.validate_on_submit():
                post.title = eform.title.data
                post.subtitle = eform.subtitle.data
                post.body = eform.body.data.replace('<p>', '').replace('</p>', '')
                post.image_url = eform.image.data
                db.session.commit()
                post_id = post.id
                return redirect(url_for('post_page', num=post_id, name=current_user.name, logged_in=current_user.is_authenticated))

            return render_template('blogging.html', bform=eform, is_edit=True, name=current_user.name, logged_in=current_user.is_authenticated)
        else:
            is_edit = "You are only authorized to edit your own posts."
            return redirect(url_for('post_page', num=post_id, is_edit=is_edit, name=current_user.name, logged_in=current_user.is_authenticated))

    # ---------------------------------  Delete PosT  -------------------------------------- #
    @app.route('/delete_post', methods=['POST', 'GET'])
    @login_required
    def delete_page():
        confirm = request.args.get('confirm')
        post_id = request.args.get('post_id')
        if not confirm:
            post_to_delete = db.session.get(BlogPosts, post_id)
            if not post_to_delete:
                flash("No posts to view!")
                return redirect(url_for('select_page', name=current_user.name, logged_in=current_user.is_authenticated))

            elif Comments.query.filter_by(post_id=post_id).first():
                flash("This post cannot be deleted!")
                return redirect(url_for('home', name=current_user.name, logged_in=current_user.is_authenticated, num=post_id))

            elif current_user.is_authenticated and current_user == post_to_delete.post_author:
                is_delete = "Are you sure of deletion?"
                return redirect(url_for('home', is_delete=is_delete, post_id=post_id, logged_in=current_user.is_authenticated))
        else:

            post_to_delete = db.session.get(BlogPosts, post_id)
            db.session.delete(post_to_delete)
            db.session.commit()
            return redirect(url_for('home', name=current_user.name, post_id=post_id, logged_in=current_user.is_authenticated))

    # ---------------------------------  Add Comment  -------------------------------------- #
    @app.route('/add_comment', methods=['POST', 'GET'])
    @login_required
    def comment_page():
        post_id = request.args.get('post_id')
        post = db.session.get(BlogPosts, post_id)
        if not post:
            return redirect(url_for('login_page', logged_in=current_user.is_authenticated))
        elif current_user.is_authenticated:
            cform = CommentsForm()
            if cform.validate_on_submit() and request.method == "POST":
                new_comment = Comments(comment_text=cform.comment_text.data.replace('<p>', '').replace('</p>', ''),
                                       comment_author=current_user,
                                       parent_post=post
                                       )
                db.session.add(new_comment)
                db.session.commit()

                return redirect(url_for('post_page', num=post_id, start_commenting=False, name=current_user.name, logged_in=current_user.is_authenticated))

            return render_template('post.html', post=post, start_commenting=True, cform=cform, name=current_user.name, logged_in=current_user.is_authenticated)

    # ---------------------------------  Delete Comment  -------------------------------------- #
    @app.route('/delete_comment', methods=['POST', 'GET'])
    @login_required
    def delete_comment():
        # confirm = request.args.get('confirm')
        comment_id = request.args.get('comment_id')
        post_id = request.args.get('post_id')
        # if not confirm:
        comment_to_delete = db.session.get(Comments, comment_id)
        if not comment_to_delete:
            return redirect(url_for('post_page', name=current_user.name, logged_in=current_user.is_authenticated, num=post_id))

        elif Replies.query.filter_by(comment_id=comment_id).first():
            flash("This comment cannot be deleted!")
            return redirect(url_for('post_page', name=current_user.name, logged_in=current_user.is_authenticated, num=post_id))

        elif current_user.is_authenticated and current_user == comment_to_delete.comment_author:
            comment_to_delete = db.session.get(Comments, comment_id)
            db.session.delete(comment_to_delete)
            db.session.commit()
            return redirect(url_for('post_page', name=current_user.name, num=post_id, logged_in=current_user.is_authenticated))

    # ---------------------------------  Add Replies  -------------------------------------- #
    @app.route('/add_replies', methods=['POST', 'GET'])
    @login_required
    def reply_page():
        comment_id = request.args.get('comment_id')
        post_id = request.args.get('post_id')
        post = db.session.get(BlogPosts, post_id)
        comment = db.session.get(Comments, comment_id)
        if not comment:
            return redirect(url_for('post_page', num=post.id, logged_in=current_user.is_authenticated))
        elif current_user.is_authenticated:
            rform = CommentsForm()
            if rform.validate_on_submit() and request.method == "POST":
                new_reply = Replies(reply_text=rform.comment_text.data.replace('<p>', '').replace('</p>', ''),
                                    reply_author=current_user,
                                    parent_comment=comment
                                    )
                db.session.add(new_reply)
                db.session.commit()

                replies_data = []
                replies = db.session.query(Replies).all()
                if replies is not None:
                    for reply in replies:
                        if reply.parent_comment == comment:
                            requested_reply = reply
                            replies_data.append(requested_reply)
                else:
                    pass
                return redirect(url_for('post_page', replies_data=replies_data, num=post_id, start_reply=False, name=current_user.name, logged_in=current_user.is_authenticated))

            return render_template('post.html', comment=comment, post=post, start_reply=True, start_commenting=False, rform=rform, logged_in=current_user.is_authenticated)

    # ---------------------------------  Delete Reply  -------------------------------------- #
    @app.route('/delete_comment/<int:reply_id>/<int:post_id>', methods=['POST', 'GET'])
    @login_required
    def delete_reply(reply_id, post_id):

        reply_to_delete = db.session.query(Replies).get(reply_id)
        if not reply_to_delete:
            flash("No reply to delete!")
            return redirect(url_for('post_page', name=current_user.name, logged_in=current_user.is_authenticated, num=post_id))

        elif current_user.is_authenticated and current_user == reply_to_delete.reply_author:
            db.session.delete(reply_to_delete)
            db.session.commit()
            return redirect(url_for('post_page', name=current_user.name, num=post_id, logged_in=current_user.is_authenticated))

    # -------------------------------- Post Details Page ---------------------------------- #
    @app.route('/post/<int:num>')
    def post_page(num):
        requested_post = None
        is_edit = request.args.get("is_edit")
        replies_data = request.args.get("replies_data")
        posts = db.session.query(BlogPosts).all()
        for post in posts:
            if post.id == num:
                requested_post = post
        comments_data = []
        comments = db.session.query(Comments).all()
        if comments is not None:
            for comment in comments:
                if comment.parent_post == requested_post:
                    gather_comment = comment
                    replies_data = []
                    replies = db.session.query(Replies).all()
                    if replies is not None:
                        for reply in replies:
                            if reply.parent_comment == gather_comment:
                                requested_reply = reply
                                replies_data.append(requested_reply)
                    comment_replies = {"comment": gather_comment, "replies": replies_data}
                    comments_data.append(comment_replies)

        return render_template('post.html', is_edit=is_edit, start_commenting=False, comments=comments_data, post=requested_post, logged_in=current_user.is_authenticated)

    # -------------------------------- Contact ----------------------------- #
    @app.route('/contact', methods=['POST', 'GET'])
    def contact_page():
        form = ContactForm()
        if form.validate_on_submit():
            name = form.name.data
            email = form.email.data
            phone = form.phone.data
            message = form.message.data
            send_email_message(name, email, phone, message)
            new_contact = Contacts(name=name,
                                   email=email,
                                   phone=phone,
                                   message=message,
                                   msg_date=datetime.now().strftime("%b %d, %y"),
                                   msg_time=datetime.now().strftime("%H:%M:%S"),
                                   )
            db.session.add(new_contact)
            db.session.commit()

            # ------------------- Clear The Form Data ----------------------- #
            form = ContactForm(formdata=None)
            return render_template('contact.html', form=form,  msg_sent=True, logged_in=current_user.is_authenticated)

        return render_template('contact.html', form=form, msg_sent=False, logged_in=current_user.is_authenticated)


    def send_email_message(name, email, phone, message):
        email_message = f"Subject:New message \n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}"
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(my_email, my_password)
            connection.sendmail(my_email, my_email, email_message)


    if __name__ == '__main__':
        app.run(debug=True)

