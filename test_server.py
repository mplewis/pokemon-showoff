from utils import shortcode
from app import app, config_app
from views import index, upload_save  # noqa

import pytest
import sure  # noqa
import hashlib
import zlib
from StringIO import StringIO
from bson.binary import Binary


class FlaskTestConfig:
    DEBUG = False
    TESTING = True


class MiscConfig:
    SHORTCODE_LEN = 12


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


class FakeMongoCollWithData:
    def __init__(self, results):
        self.storage = {}
        self.results = results

    def insert(self, item):
        self.last_inserted = item
        pass

    def find(self, query):
        self.last_find_query = query
        return FakeMongoFindResultsWithData(self.results)


class FakeMongoFindResultsWithData:
    def __init__(self, results):
        self.results = results

    def count(self):
        return len(self.results)

    def __getitem__(self, pos):
        return self.results[pos]


def client():
    config_app(flask_config=FlaskTestConfig, misc_config=MiscConfig)
    return app.test_client()


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
    s = client()

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

    r.status_code.should.equal(302)
    headers = {}
    for header in r.headers:
        key, val = header
        headers[key] = val
    headers.should.have.key('Location')

    fake_coll.last_find_query.should.equal({'md5': md5})
    inserted = fake_coll.last_inserted
    inserted.should.have.key('md5').with_value.being.equal(stored['md5'])
    (inserted.should.have.key('save_data_zlib')
     .with_value.being.equal(stored['save_data_zlib']))
    inserted.should.have.key('shortcode')
    inserted.should.have.key('created')
    inserted['created'].should.be.a('datetime.datetime')
    inserted['shortcode'].should.have.length_of(MiscConfig.SHORTCODE_LEN)

    if restore:
        app.mongo_coll = old_coll


def test_post_one_exists():
    s = client()

    fake_data = {'md5': 'd41d8cd98f00b204e9800998ecf8427e',
                 'shortcode': 'some_shortcode',
                 'save_data_zlib': None}
    fake_coll = FakeMongoCollWithData([fake_data])
    app.mongo_coll = fake_coll

    with open('test_save.sav', 'rb') as f:
        raw_data = f.read()

    hasher = hashlib.md5()
    hasher.update(raw_data)
    md5 = hasher.hexdigest()

    with open('test_save.sav', 'rb') as f:
        data = {'save': (f, 'tpp.sav')}
        r = s.post('/', data=data)

    r.status_code.should.equal(302)
    headers = {}
    for header in r.headers:
        key, val = header
        headers[key] = val
    headers.should.have.key('Location')
    headers['Location'].endswith('/some_shortcode').should.be.true
    fake_coll.last_find_query.should.equal({'md5': md5})


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


def test_get_team():
    s = client()

    with open('test_save.sav', 'rb') as f:
        save_data_zlib = zlib.compress(f.read())
    fake_data = {'md5': 'd41d8cd98f00b204e9800998ecf8427e',
                 'shortcode': 'some_shortcode',
                 'save_data_zlib': save_data_zlib}
    fake_coll = FakeMongoCollWithData([fake_data])
    app.mongo_coll = fake_coll

    r = s.get('/' + fake_data['shortcode'])

    r.status_code.should.equal(200)
    r.data.should.equal('Trainer name: RED')


def test_shortcode():
    vowels = 'aeiou'
    consonants = 'bcdfghjklmnpqrstvwxyz'
    c = shortcode(length=10)
    c.should.have.length_of(10)
    for letter in c[::2]:
        letter.should.be.within(consonants)
    for letter in c[1::2]:
        letter.should.be.within(vowels)
    d = shortcode(start_with_vowel=True)
    d.should.have.length_of(12)
    for letter in d[::2]:
        letter.should.be.within(vowels)
    for letter in d[1::2]:
        letter.should.be.within(consonants)
