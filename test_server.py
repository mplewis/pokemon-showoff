import pytest
import sure  # noqa
import hashlib
import zlib
from StringIO import StringIO
from bson.binary import Binary


class FlaskTestConfig:
    DEBUG = False
    TESTING = True


class FakeMongoColl:
    def __init__(self, num_results):
        self.storage = {}
        self.num_results = num_results

    def insert(self, item):
        self.last_inserted = item
        pass

    def find(self, query):
        self.last_find_query = query
        return FakeMongoFindResults(self.num_results)


class FakeMongoFindResults:
    def __init__(self, num_results):
        self.num_results = num_results

    def count(self):
        return self.num_results


@pytest.fixture
def client():
    from app import app, config_app
    from views import index, upload_save  # noqa
    config_app(flask_config=FlaskTestConfig)
    return app.test_client()


@pytest.fixture
def client_and_app():
    from app import app, config_app
    from views import index, upload_save  # noqa
    config_app(flask_config=FlaskTestConfig)
    return (app.test_client(), app)


def test_index():
    s = client()
    r = s.get('/')
    r.status_code.should.equal(200)


def test_post_none():
    s = client()
    r = s.post('/')
    r.status_code.should.equal(400)
    r.data.should.equal('Expected 1 file, received 0 files.')


def test_post_one():
    s, app = client_and_app()

    restore = False
    if hasattr(app, 'mongo_coll'):
        restore = True
        old_coll = app.mongo_coll

    fake_coll = FakeMongoColl(0)
    app.mongo_coll = fake_coll

    with open('test_save.sav', 'rb') as f:
        raw_data = f.read()

    hasher = hashlib.md5()
    hasher.update(raw_data)
    md5 = hasher.hexdigest()

    compressed = zlib.compress(raw_data)

    with open('test_save.sav', 'rb') as f:
        data = {'save': (f, 'tpp.sav')}
        r = s.post('/', data=data)

    stored = {'md5': md5, 'save_data_zlib': Binary(compressed)}

    r.data.should.equal(md5)
    r.status_code.should.equal(200)
    fake_coll.last_find_query.should.equal({'md5': md5})
    fake_coll.last_inserted.should.equal(stored)

    if restore:
        app.mongo_coll = old_coll


def test_post_one_exists():
    s, app = client_and_app()

    restore = False
    if hasattr(app, 'mongo_coll'):
        restore = True
        old_coll = app.mongo_coll

    fake_coll = FakeMongoColl(1)
    app.mongo_coll = fake_coll

    with open('test_save.sav', 'rb') as f:
        raw_data = f.read()

    hasher = hashlib.md5()
    hasher.update(raw_data)
    md5 = hasher.hexdigest()

    with open('test_save.sav', 'rb') as f:
        data = {'save': (f, 'tpp.sav')}
        r = s.post('/', data=data)

    r.data.should.equal('Save file already exists')
    r.status_code.should.equal(400)
    fake_coll.last_find_query.should.equal({'md5': md5})

    if restore:
        app.mongo_coll = old_coll


def test_post_one_malformed():
    s = client()
    data = {'save': (StringIO('not a save file'), 'tpp.sav')}
    r = s.post('/', data=data)
    r.status_code.should.equal(400)
    r.data.should.equal('Could not parse save file')


def test_post_two():
    s = client()
    files = {'save1': (StringIO('one save file'), 'file.sav'),
             'save2': (StringIO('another save file'), 'file.sav')}
    r = s.post('/', data=files)
    r.status_code.should.equal(400)
    r.data.should.equal('Expected 1 file, received 2 files.')
