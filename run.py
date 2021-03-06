# coding=utf-8
from flask import Flask, render_template, session, redirect, url_for, flash
# 引入Bootstrap模板
from flask.ext.bootstrap import Bootstrap
# 使用flask-Moment本地化日期和时间，引入 moment.js 库
from flask.ext.moment import Moment
from datetime import datetime
# 引入表单
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, FileField, SelectField, TextAreaField, PasswordField
from wtforms.validators import Required
# 配置sqlite数据库
import os
from flask.ext.sqlalchemy import SQLAlchemy
# 使用Flask-Migrate实现数据库迁移
from flask.ext.migrate import Migrate, MigrateCommand
# 发送电子邮件功能
from flask.ext.mail import Message, Mail
# 异步发送邮件
from threading import Thread

# 获取文件当前目录
basedir = os.path.abspath(os.path.dirname(__file__))

# 初始化Flask
app = Flask(__name__)
# 跨站请求伪造保护
app.config['SECRET_KEY'] = 'hard to guess string'
# 初始化数据库
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', True)
SQLALCHEMY_TRACK_MODIFICATIONS = False
db = SQLAlchemy(app)
# 初始化Bootstrap
bootstrap = Bootstrap(app)
# 初始化Moment
moment = Moment(app)
# 邮件支持
mail = Mail(app)
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <flasky@example.com>'


# 异步发送
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    # 调用线程发送，移到后台
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
    # mail.send(msg)


# 重定向和用户会话
@app.route('/', methods=['GET', 'POST'])
def index():
    # 处理NameForm表单，在index.html中渲染
    form = NameForm()
    # validate_on_submit函数验证是否登录
    if form.validate_on_submit():
        # 提交表单后，程序会使用 filter_by() 查询过滤器在数据库中查找提交的名字
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            # 变量 known 被写入用户会话中，因此重定向之后，可以把数据传给模板，用来显示自定义的欢迎消息。
            session['known'] = False
            # 电子邮件发送处理
            if app.config['FLASK_ADMIN']:
                send_email(app.config['FLASK_ADMIN'], 'New User',
                           'mail/new_user', user=user)
        else:
            session['known'] = True
        # 使用session保存输入的数据
        session['name'] = form.name.data
        form.name.data = ''
        # 重定向函数index （Post/ 重定向 /Get 模式）
        return redirect(url_for('index'))
    return render_template('index.html',
                           # 加入一个datetime变量，在index页面查看渲染
                           current_time=datetime.utcnow(),
                           # 直接从会话中读取name参数的值
                           form=form, name=session.get('name'),
                           known=session.get('known', False)
                           )


# file upload
@app.route('/file', methods=['GET', 'POST'])
def file():
    filename = None;
    form = FileForm()
    if form.validate_on_submit():
        filename = form.filename.data
        form.filename.data = ''
    return render_template('file.html', form=form, filename=filename)


# select
@app.route('/select', methods=['GET', 'POST'])
def select():
    selectname = None;
    form = SelectForm()
    if form.validate_on_submit():
        selectname = form.selectname.data
        form.selectname.data = ''
    return render_template('select.html', form=form, selectname=selectname)


# textarea
@app.route('/textarea', methods=['GET', 'POST'])
def text():
    textarea = None;
    form = TextArea()
    if form.validate_on_submit():
        textarea = form.textarea.data
        form.textarea.data = ''
    return render_template('textarea.html', form=form, textarea=textarea)


# user路由
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


# 内网url
@app.route('/url')
def url():
    return render_template('url.html')


# 自定义404页面
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('405.html'), 405


# user表单类
class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class FileForm(Form):
    filename = FileField('Please select file name:', validators=[Required()])
    submit = SubmitField('Submit')


class SelectForm(Form):
    selectname = SelectField('select:', validators=[Required()])
    submit = SubmitField('Submit')


class TextArea(Form):
    textarea = TextAreaField('this is textarea!', validators=[Required()])
    submit = SubmitField('Submit')


# SQL模型
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    # 关系使用 users 表中的外键连接了两行。添加到 User 模型中的 role_id 列被定义为外键， 就是这个外键建立起了关系
    # 传给 db.ForeignKey() 的参数 'roles.id' 表明，这列的值是 roles 表中行的 id 值
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


# 启动
if __name__ == '__main__':
    app.run(debug=True, port=80)
