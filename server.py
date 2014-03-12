from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    import config
    app.config.from_object(config.FlaskConfig)
    app.run()
