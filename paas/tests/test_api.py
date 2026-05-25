import pytest
from sqlmodel import Session, select

from paas.database.db_models import Links


@pytest.fixture
def test_link(session: Session):
    """Создает одну базовую ссылку в памяти для тестов чтения, обновления и удаления."""
    link = Links(
        original_url="https://hexlet.io",
        short_name="hex",
        short_url="http://localhost:8080/r/hex"
    )
    session.add(link)
    session.commit()
    return link


def test_get_all_links_success(client, test_link):
    response = client.get('/api/links')
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["short_name"] == "hex"


def test_link_by_id_success(client, test_link):
    response = client.get(f'/api/links/{test_link.id}')
    assert response.status_code == 200

    data = response.get_json()
    assert data["id"] == test_link.id
    assert data["original_url"] == "https://hexlet.io"


def test_link_by_id_not_found(client):
    response = client.get('/api/links/9999')
    assert response.status_code == 404


def test_create_link_success(client, session: Session):
    payload = {
        "original_url": "https://google.com",
        "short_name": "goog"
    }
    response = client.post('/api/links', json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert data["id"] is not None
    assert data["short_name"] == "goog"
    assert data["short_url"] == "http://localhost:8080/r/goog"

    session.expire_all()
    db_link = session.exec(select(Links).where(Links.short_name == "goog")).first()
    assert db_link is not None


def test_create_link_validation_blank(client):
    payload = {"original_url": "", "short_name": ""}
    response = client.post('/api/links', json=payload)
    assert response.status_code == 422


def test_create_link_validation_special_symbols(client):
    payload = {"original_url": "https://yandex.ru", "short_name": "ya/link"}
    response = client.post('/api/links', json=payload)
    assert response.status_code == 422


def test_create_link_duplicate_error(client, session: Session):
    existing_link = Links(
        original_url="https://a.com",
        short_name="clone",
        short_url="http://localhost:8080/r/clone"
    )
    session.add(existing_link)
    session.commit()

    payload = {"original_url": "https://b.com", "short_name": "clone"}
    response = client.post('/api/links', json=payload)
    assert response.status_code == 422


def test_link_update_success(client, session: Session, test_link):
    payload = {
        "original_url": "https://ru.hexlet.io",
        "short_name": "hexnew"
    }
    response = client.put(f'/api/links/{test_link.id}', json=payload)
    assert response.status_code == 200

    data = response.get_json()
    assert data["original_url"] == "https://ru.hexlet.io"
    assert data["short_name"] == "hexnew"

    session.expire_all()
    db_link = session.exec(select(Links).where(Links.id == test_link.id)).first()
    assert db_link.short_name == "hexnew"


def test_link_delete_success(client, session: Session, test_link):
    link_id = test_link.id

    response = client.delete(f'/api/links/{link_id}')
    assert response.status_code == 204
    assert response.data == b''

    session.expire_all()
    db_link = session.exec(select(Links).where(Links.id == link_id)).first()
    assert db_link is None


def test_links_pagination_success(client, session: Session):
    links = [
        Links(
            original_url=f"https://example.com/{i}",
            short_name=f"link{i}",
            short_url=f"http://localhost:8080/r/link{i}"
        )
        for i in range(1, 12)
    ]
    session.add_all(links)
    session.commit()

    response = client.get('/api/links?range=[5,10]')
    assert response.status_code == 200

    assert response.headers.get('Content-Range') == "links 5-10/11"

    data = response.get_json()
    assert len(data) == 5

    short_names = [item["short_name"] for item in data]
    assert "link1" not in short_names
