from flask import Flask, redirect

app = Flask(__name__)


@app.route('/')
def main_redirect():
    return redirect('/ping')


@app.get('/ping')
def ping_pong():
    return 'pong'


if __name__ == '__main__':
    app.run(debug=True)
