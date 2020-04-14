# Import libraries
import os
from flask import Flask, render_template, redirect, abort, request
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
    s = request.args.get('s')
    if s:
        news = session.query(News).filter(News.title.contains(s), News.is_private == False).all()
        return render_template("index.html", news=news, title='Search returned: ', site='Search')
    else:
        news = session.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news, title='All posts', site='Posts')


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
                               message="Invalid username or password.",
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
    return render_template('news_output.html', news=news, admin=' | [for_admin]')


@app.route('/users_post/', methods=['GET', 'POST'])
def user_post():
    session = db_session.create_session()
    news = session.query(News).filter(News.is_private == True)
    return render_template('index.html', news=news, title='Users posts(Not public)', site='User Posts')


@app.route('/post_output_public/<int:id>', methods=['GET', 'POST'])
def user_posts_public(id):
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id).first()
    news.is_private = False
    session.commit()
    return redirect('/')


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
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_news.html', title='Post edit', form=form)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)