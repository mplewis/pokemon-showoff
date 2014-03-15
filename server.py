from utils import unmulti
from pokemon_save_parser.save_parser import SaveDataGen1

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
    upload_name = uploaded.keys()[0]
    upload_file = uploaded[upload_name]
    upload_data = upload_file.read()
    try:
        save = SaveDataGen1(upload_data)
    except Exception:
        return 'Could not parse save file', 400
    return save.trainer_name


if __name__ == '__main__':
    import config
    app.config.from_object(config.FlaskConfig)
    app.run()
