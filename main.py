# Import libraries
import os
from flask import Flask, render_template, redirect, abort, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import random
# Import files
from data import db_session
from data.forms import LoginForm, RegisterForm, NewsForm, Comment
from data.news import News
from data.users import User
from data.comments import Comments

# Main site parameters
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandex'
db_session.global_init('db/blog.sqlite')
# Used for login users
login_manager = LoginManager()
login_manager.init_app(app)


# Main page, where appear all posts
@app.route('/')
def index():
    session = db_session.create_session()
    # Get search data
    s = request.args.get('s')
    # If the search bar is not empty
    if s:
        news = session.query(News).filter(News.title.contains(s), News.is_private == False, News.to_rabbit == False).all()
        return render_template("index.html", news=news, title='Search returned: ', site='Search')
    else:
        news = session.query(News).filter(News.is_private != True, News.to_rabbit == False)
    return render_template("index.html", news=news, title='All posts', site='Posts')


# Need for users login
@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


# Login users, and add in table
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Invalid username or password.",
                               form=form)
    return render_template('login.html', form=form)


# Logout users
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# Register users
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   form=form,
                                   message="Passwords don't match")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html',
                                   form=form,
                                   message="This user already exists")
        user = User(
            name=form.name.data,
            email=form.email.data,

        )
        user.is_admin = form.is_admin.data
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', form=form)


# Add new news
@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.description = form.description.data
        news.to_rabbit = form.to_rabbit.data
        # News to rabbit not private
        if news.to_rabbit:
            news.is_private = False
        session.merge(news)
        session.commit()
        return redirect('/')
    return render_template('add_news.html',
                           form=form)


# News output
@app.route('/post_output/<int:id>', methods=['GET', 'POST'])
def news_output(id):
    session = db_session.create_session()
    form = Comment()
    news = session.query(News).filter(News.id == id)
    comments = session.query(Comments).filter(Comments.post_id == id)
    # Comments
    if form.validate_on_submit():
        comment = Comments()
        comment.comment_content = form.comment_content.data
        # If user not login or register, his username is User + random number
        if not current_user.is_authenticated:
            comment.user_name = 'User' + str(random.randrange(100, 999))
        # If user is login or register
        elif current_user.is_authenticated:
            comment.user_name = current_user.name
        comment.post_id = id
        session.merge(comment)
        session.commit()
        return render_template('news_output.html', news=news, form=form, admin=' | [for_admin]', comments=comments)
    return render_template('news_output.html', news=news, form=form, admin=' | [for_admin]', comments=comments)


# Output news only for admin
@app.route('/users_post/', methods=['GET', 'POST'])
def user_post():
    session = db_session.create_session()
    news = session.query(News).filter(News.is_private == True, News.to_rabbit == False)
    return render_template('index.html', news=news, title='Users posts(Not public)', site='User Posts')


# All news is not private
@app.route('/post_output_public/<int:id>', methods=['GET', 'POST'])
def user_posts_public(id):
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id).first()
    news.is_private = False
    session.commit()
    return redirect('/')


# News delete
@app.route('/post_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id).first()
    if news:
        session.delete(news)
        session.commit()
    else:
        abort(404)
    return redirect('/')


# Edit news
@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id).first()
        if news:
            form.title.data = news.title
            form.description.data = news.description
            form.content.data = news.content
            form.to_rabbit.data = news.to_rabbit
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          News.user == current_user).first()
        if news:
            news.title = form.title.data
            news.description = form.description.data
            news.content = form.content.data
            news.to_rabbit = form.to_rabbit.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_news.html', title='Post edit', form=form)


# Output rabbit traps. These are just questions
@app.route('/rabbit')
def main_rabbit():
    session = db_session.create_session()
    rabbit = session.query(News).filter(News.to_rabbit == True)
    return render_template('index.html', news=rabbit, title='Rabbit', site='Rabbit', admin=' | [for_admin]')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)