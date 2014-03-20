from pokemon_save_parser.save_parser import SaveDataGen1
from utils import unmulti, shortcode
from app import app

import zlib
import hashlib
from flask import render_template, request, redirect
from bson.binary import Binary
from datetime import datetime


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

    existing = app.mongo_coll.find({'md5': md5})
    if existing.count() > 0:
        existing_shortcode = existing[0]['shortcode']
        return redirect('/' + existing_shortcode)

    stored_shortcode = shortcode(app.misc_config.SHORTCODE_LEN)
    storable = {'md5': md5,
                'shortcode': stored_shortcode,
                'save_data_zlib': Binary(compressed),
                'created': datetime.now()}
    app.mongo_coll.insert(storable)

    return redirect('/' + stored_shortcode)


@app.route('/<shortcode>', methods=['GET'])
def show_team(shortcode):
    existing = app.mongo_coll.find({'shortcode': shortcode})
    if existing.count() == 0:
        return 'No team found with shortcode %s' % shortcode, 404

    save_data_compressed = existing[0]['save_data_zlib']
    save_data = zlib.decompress(save_data_compressed)
    save = SaveDataGen1(save_data)

    return 'Trainer name: %s' % save.trainer_name
