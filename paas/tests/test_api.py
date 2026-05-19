import pytest
from sqlmodel import SQLModel, create_engine
from paas.scripts.app import app
from ..database import db_engine, db_models


@pytest.fixture
def client():
    """Тестовый клиент с временной БД в памяти"""
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(test_engine)

    original_engine = db_engine
    try:
        import paas.database.db_connection as dbc
        dbc.db_engine = test_engine
        app.config['TESTING'] = True
        app.config['BASE_URL'] = 'http://localhost:8080'
        with app.test_client() as client:
            yield client
    finally:
        dbc.db_engine = original_engine


def test_get_links_empty(client):
    response = client.get('/api/links')
    assert response.status_code == 200
    assert response.json == []


def test_create_link(client):
    data = {
        "original_url": "https://example.com",
        "short_name": "exmpl"
    }
    response = client.post('/api/links', json=data)
    assert response.status_code == 201
    json_data = response.json
    assert json_data['original_url'] == data['original_url']
    assert json_data['short_name'] == data['short_name']
    assert json_data['short_url'] == 'http://localhost:8080/r/exmpl'
    assert 'id' in json_data


def test_create_duplicate_short_name(client):
    client.post('/api/links', json={
        "original_url": "https://first.com",
        "short_name": "dup"
    })
    response = client.post('/api/links', json={
        "original_url": "https://second.com",
        "short_name": "dup"
    })
    assert response.status_code == 409
    assert response.json['error'] == 'short_name already exists'


def test_get_link_by_id(client):
    post_resp = client.post('/api/links', json={
        "original_url": "https://example.com",
        "short_name": "testid"
    })
    link_id = post_resp.json['id']

    response = client.get(f'/api/links/{link_id}')
    assert response.status_code == 200
    assert response.json['id'] == link_id


def test_get_link_not_found(client):
    response = client.get('/api/links/9999')
    assert response.status_code == 404
    assert response.json['error'] == 'Not found'


def test_update_link(client):
    post_resp = client.post('/api/links', json={
        "original_url": "https://old.com",
        "short_name": "update"
    })
    link_id = post_resp.json['id']

    response = client.put(f'/api/links/{link_id}', json={
        "original_url": "https://new.com",
        "short_name": "updated"
    })
    assert response.status_code == 200
    assert response.json['original_url'] == 'https://new.com'
    assert response.json['short_name'] == 'updated'
    assert response.json['short_url'] == 'http://localhost:8080/r/updated'


def test_update_link_conflict(client):
    client.post('/api/links', json={
        "original_url": "https://a.com",
        "short_name": "first"
    })
    post2 = client.post('/api/links', json={
        "original_url": "https://b.com",
        "short_name": "second"
    })
    link2_id = post2.json['id']

    response = client.put(f'/api/links/{link2_id}', json={"short_name": "first"})
    assert response.status_code == 409
    assert response.json['error'] == 'short_name already exists'


def test_delete_link(client):
    post_resp = client.post('/api/links', json={
        "original_url": "https://example.com",
        "short_name": "todelete"
    })
    link_id = post_resp.json['id']

    response = client.delete(f'/api/links/{link_id}')
    assert response.status_code == 204

    get_resp = client.get(f'/api/links/{link_id}')
    assert get_resp.status_code == 404


def test_delete_not_found(client):
    response = client.delete('/api/links/9999')
    assert response.status_code == 404


def test_redirect_to_original(client):
    client.post('/api/links', json={
        "original_url": "https://example.com",
        "short_name": "redirect"
    })
    response = client.get('/r/redirect')
    assert response.status_code == 302
    assert response.headers['Location'] == 'https://example.com'


def test_redirect_not_found(client):
    response = client.get('/r/nonexistent')
    assert response.status_code == 404


def test_html_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Link Shortener' in response.data


def test_html_list_links(client):
    client.post('/api/links', json={
        "original_url": "https://html-test.com",
        "short_name": "htmltest"
    })
    response = client.get('/links')
    assert response.status_code == 200
    assert b'All Short Links' in response.data
    assert b'htmltest' in response.data


def test_html_create_link_form(client):
    response = client.get('/links/new')
    assert response.status_code == 200
    assert b'Create New Link' in response.data