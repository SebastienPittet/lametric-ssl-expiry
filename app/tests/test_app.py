from flask import Flask
import pytest

app = Flask(__name__)
app.testing = True

@pytest.fixture
def test_content_OK():
    with app.test_client() as c:
        response = c.get('/test')
        assert response.status_code == 200
        assert b'OK!' in response.data
