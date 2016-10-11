# coding=utf-8
from flask import Flask, render_template, session, redirect, url_for
# 引入Bootstrap模板
from flask.ext.bootstrap import Bootstrap
# 使用flask-Moment本地化日期和时间，引入 moment.js 库
from flask.ext.moment import Moment
from datetime import datetime
# 引入表单
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

# 初始化Flask
app = Flask(__name__)
# 跨站请求伪造保护
app.config['SECRET_KEY'] = 'hard to guess string'
# 初始化Bootstrap
bootstrap = Bootstrap(app)
# 初始化Moment
moment = Moment(app)


# 重定向和用户会话
@app.route('/', methods=['GET', 'POST'])
def index():
    # 处理NameForm表单，在index.html中渲染
    form = NameForm()
    # validate_on_submit函数验证是否登录
    if form.validate_on_submit():
        # 使用session保存输入的数据
        session['name'] = form.name.data
        # 重定向函数index （Post/ 重定向 /Get 模式）
        return redirect(url_for('index'))
    return render_template('index.html',
                           # 加入一个datetime变量，在index页面查看渲染
                           current_time=datetime.utcnow(),
                           # 直接从会话中读取name参数的值
                           form=form, name=session.get('name')
                           )


# user路由
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


# 自定义404页面
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# user表单类
class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

# 启动
if __name__ == '__main__':
    app.run(debug=True, port=80)
