#import unittest
import app


def test_flaskapp():
    response = app.app.test_client().get('/test')
    assert response.status_code == 200
    assert response.data == b'OK!'
