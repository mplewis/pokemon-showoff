from app import app, config_app
from views import index, upload_save  # noqa

if __name__ == '__main__':
    import config
    config_app(flask_config=config.FlaskConfig,
               mongo_db_config=config.MongoDbConfig,
               misc_config=config.MiscConfig)
    app.run()
