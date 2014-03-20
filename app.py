from flask import Flask
from pymongo import MongoClient


app = Flask(__name__)


def config_app(flask_config=None, mongo_db_config=None, mongo_coll_obj=None,
               misc_config=None):
    if flask_config:
        app.config.from_object(flask_config)

    if mongo_db_config and mongo_coll_obj:
        raise ValueError('Cannot pass in both mongo_db_config and '
                         'mongo_coll_obj')
    elif mongo_db_config:
        app.mongo_client = MongoClient(mongo_db_config.uri)
        app.mongo_db = app.mongo_client[mongo_db_config.db]
        app.mongo_coll = app.mongo_db[mongo_db_config.coll]
    elif mongo_coll_obj:
        app.mongo_coll = mongo_coll_obj

    if misc_config:
        app.misc_config = misc_config
