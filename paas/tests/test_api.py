import pytest
from sqlmodel import Session, select

from paas.database.db_models import Links


def test_add_link_page(client):
    response = client.get('/api/links/new')
    assert response.status_code == 200


def test_create_link_success(client, session: Session):
    payload = {
        "original_url": "https://google.com",
        "short_name": "goog"
    }
    response = client.post('/api/links', data=payload)
    assert response.status_code == 302

    session.expire_all()
    db_link = session.exec(select(Links).where(Links.short_name == "goog")).first()

    assert db_link is not None
    assert db_link.original_url == "https://google.com"


def test_create_link_validation_blank(client):
    payload = {"original_url": "", "short_name": ""}
    response = client.post('/api/links', data=payload)
    assert response.status_code == 422
    assert "form" in response.data.decode('utf-8').lower()


def test_create_link_validation_special_symbols(client):
    payload = {"original_url": "https://yandex.ru", "short_name": "ya/link"}
    response = client.post('/api/links', data=payload)
    assert response.status_code == 422


def test_create_link_duplicate_error(client, session: Session):
    existing_link = Links(
        original_url="https://a.com",
        short_name="clone",
        short_url="http://localhost:8080/clone"
    )
    session.add(existing_link)
    session.commit()

    payload = {"original_url": "https://b.com", "short_name": "clone"}
    response = client.post('/api/links', data=payload)
    assert response.status_code == 422


@pytest.fixture
def test_link(session: Session):
    link = Links(
        original_url="https://hexlet.io",
        short_name="hex",
        short_url="http://localhost:8080/hex"
    )
    session.add(link)
    session.commit()
    return link


def test_link_index_page(client, test_link):
    response = client.get(f'/api/links/{test_link.id}')
    assert response.status_code == 200


def test_link_index_not_found(client):
    response = client.get('/api/links/9999')
    assert response.status_code == 404


def test_edit_page_opens(client, test_link):
    response = client.get(f'/api/links/{test_link.id}/update')
    assert response.status_code == 200


def test_link_patch_success(client, session: Session, test_link):
    payload = {
        "original_url": "https://ru.hexlet.io",
        "short_name": "hexnew"
    }
    response = client.post(f'/api/links/{test_link.id}/update', data=payload)
    assert response.status_code == 302

    session.expire_all()
    db_link = session.exec(select(Links).where(Links.id == test_link.id)).first()
    assert db_link.original_url == "https://ru.hexlet.io"
    assert db_link.short_name == "hexnew"


def test_delete_confirm_flashes_message(client, test_link):
    response = client.get(f'/api/links/{test_link.id}/delete_confirm')
    assert response.status_code == 302


def test_actual_delete_removes_from_db(client, session: Session, test_link):
    link_id = test_link.id

    response = client.get(f'/api/links/{link_id}/delete')
    assert response.status_code == 302

    session.expire_all()
    db_link = session.exec(select(Links).where(Links.id == link_id)).first()
    assert db_link is None

def test_links_pagination_success(client, session: Session):
    link1 = Links(original_url="https://one.com", short_name="one", short_url="http://localhost:8080/one")
    link2 = Links(original_url="https://two.com", short_name="two", short_url="http://localhost:8080/two")
    link3 = Links(original_url="https://three.com", short_name="three", short_url="http://localhost:8080/three")
    
    session.add_all([link1, link2, link3])
    session.commit()

    response = client.get('/api/links?range=[1,3]')
    assert response.status_code == 200

    html_content = response.data.decode('utf-8')

    assert "two" in html_content
    assert "three" in html_content
    
    assert "one" not in html_content