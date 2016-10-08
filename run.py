# coding=utf-8
from flask import Flask, render_template
# 引入Bootstrap模板
from flask.ext.bootstrap import Bootstrap
# 本地化日期和时间
from flask.ext.moment import Moment
from datetime import datetime

# 初始化Flask
app = Flask(__name__)
# 初始化Bootstrap
bootstrap = Bootstrap(app)
moment = Moment(app)

# index路由
@app.route('/')
def index():
    return render_template('index.html',
                           current_time=datetime.utcnow())


# user路由
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


# 自定义404页面
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# 启动
if __name__ == '__main__':
    app.run(debug=True, port=80)
