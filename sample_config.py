class MongoDbConfig:
    uri = 'mongodb://my-mongo-server.com/mydb'  # noqa
    db = 'pokemon_showoff'
    coll = 'save_files'


class FlaskConfig:
    DEBUG = False
    SERVER_NAME = 'localhost:5000'
