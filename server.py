from flask import Flask, render_template, abort

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_save():
    return abort(500)


if __name__ == '__main__':
    import config
    app.config.from_object(config.FlaskConfig)
    app.run()
