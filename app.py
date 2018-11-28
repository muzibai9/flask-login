# -*- coding:utf-8 -*-
from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, EqualTo
from flask_migrate import Migrate, MigrateCommand
import os


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hard to guess string'

db = SQLAlchemy(app)
manager = Manager(app)
bootstrap = Bootstrap(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))

    def __repr__(self):
        return '<User %r>' % self.username


class LoginForm(Form):
    username = StringField(u"用户名", validators=[DataRequired()])
    password = PasswordField(u"密码", validators=[DataRequired()])
    submit = SubmitField(u"登入")


class RegistrationForm(Form):
    username = StringField(u"用户名", validators=[DataRequired()])
    password = PasswordField(u"密码", validators=[DataRequired(), EqualTo('password2', message=u"两次密码必须一样")])
    password2 = PasswordField(u"密码确认", validators=[DataRequired()])
    submit = SubmitField(u"注册")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u"用户名正在被使用")


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        password = form.password.data
        if user is not None:
            if password == user.password:
                return render_template('login.html')
    return render_template('index.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


if __name__ == '__main__':
    manager.run()
