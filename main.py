# Import libraries
import os
from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
# Import files
from data import db_session
from data.forms import LoginForm, RegisterForm, NewsForm
from data.news import News
from data.users import User

# Main site parameters
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandex'
db_session.global_init('db/blog.sqlite')
# Used for login users
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def index():
    session = db_session.create_session()
    news = session.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news, title='Посты')


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


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
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html',
                                   form=form,
                                   message="Такой пользователь уже есть")
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
        current_user.news.append(news)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('add_news.html',
                           form=form)


@app.route('/post_output/<int:id>', methods=['GET', 'POST'])
def news_output(id):
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id)
    return render_template('news_output.html', news=news)


@app.route('/users_post/', methods=['GET', 'POST'])
def user_post():
    session = db_session.create_session()
    news = session.query(News).filter(News.is_private == True)
    return render_template('index.html', news=news, title='Посты пользователей')


@app.route('/post_output/<int:id>', methods=['GET', 'POST'])
def news_output_admin(id):
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id and News.is_private == True)
    return render_template('news_output.html', news=news, admin=' | [for admin]')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
