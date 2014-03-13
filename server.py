from utils import unmulti

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_save():
    uploaded = unmulti(request.files)
    if len(uploaded) != 1:
        return 'Expected 1 file, received %s files.' % len(uploaded), 400
    return 'OK'


if __name__ == '__main__':
    import config
    app.config.from_object(config.FlaskConfig)
    app.run()
