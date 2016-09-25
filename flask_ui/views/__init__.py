from flask_ui import app


@app.route('/')
def init():
    return '<h1>Welcome to Autoexam</h1>'
