from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return 'hello world'


@app.route('/user/<name>')
def user(name):
    return 'hello %s!' % name

if __name__ == '__main__':
    app.run(debug=True, port=80)
