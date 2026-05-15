from paas.tests import app


def test_ping_endpoint():
    with app.test_client() as client:
        response = client.get('/ping')
        assert response.status_code == 200
        assert response.data.decode('utf-8') == 'pong'


def test_ping_post_not_allowed():
    with app.test_client() as client:
        response = client.post('/ping')
        assert response.status_code == 405
