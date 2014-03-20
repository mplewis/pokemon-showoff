from pokemon_save_parser.save_parser import SaveDataGen1
from utils import unmulti, shortcode
from app import app

import zlib
import hashlib
from flask import render_template, request
from bson.binary import Binary


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
        SaveDataGen1(upload_data)
    except Exception:
        return 'Could not parse save file', 400

    hasher = hashlib.md5()
    hasher.update(upload_data)
    md5 = hasher.hexdigest()

    compressed = zlib.compress(upload_data)

    if app.mongo_coll.find({'md5': md5}).count() > 0:
        return 'Save file already exists', 400

    storable = {'md5': md5,
                'shortcode': shortcode(app.misc_config.SHORTCODE_LEN),
                'save_data_zlib': Binary(compressed)}
    app.mongo_coll.insert(storable)

    return md5
