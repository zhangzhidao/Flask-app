# coding=utf-8
from flask import Flask, render_template
# 引入Bootstrap模板
from flask.ext.bootstrap import Bootstrap

# 初始化Flask
app = Flask(__name__)
# 初始化Bootstrap
bootstrap = Bootstrap(app)


# index路由
@app.route('/')
def index():
    return render_template('index.html')


# user路由
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# 启动
if __name__ == '__main__':
    app.run(debug=True, port=80)
