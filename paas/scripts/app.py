import os
from ast import literal_eval

from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlmodel import Session, func, select

from ..database import create_db_and_tables, db_engine, db_models
from .validator import validate

create_db_and_tables()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
CORS(
    app,
    resources={r"/api/*": {"origins": "http://localhosts:5173"}},
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

@app.get('/ping')
def ping_pong():
    return 'pong', 200

@app.route('/api/links')
def get_links():
    range_str = request.args.get('range')

    if not range_str:
        with Session(db_engine) as session:
            links = session.exec(
                select(db_models.Links)
                .order_by(db_models.Links.created_at)
                ).all()

        return jsonify([link.model_dump() for link in links]), 200

    try:
        parsed_range = literal_eval(range_str)
        start = int(parsed_range[0])
        end = int(parsed_range[1])
    except (ValueError, SyntaxError, IndexError, TypeError):
        start, end = 0, 10

    limit_count = end - start

    with Session(db_engine) as session:
        total_links = session.exec(select(func.count(db_models.Links.id))).one()

        links = session.exec(
            select(db_models.Links)
            .order_by(db_models.Links.created_at)
            .offset(start)
            .limit(limit_count)
        ).all()

    links_list = [link.model_dump() for link in links]

    response = app.make_response(jsonify(links_list))
    response.headers['Content-Range'] = f"links {start}-{end}/{total_links}"
    response.headers['Content-Type'] = 'application/json'
    return response, 200


@app.post('/api/links')
def create_link():
    data = request.get_json() or {}
    errors = validate(data)

    short_name = data.get('short_name')

    with Session(db_engine) as session:
        if session.exec(select(db_models.Links)
                .where(db_models.Links.short_name == short_name)
                ).first():
            errors['unique_name'] = "This name already exists"

    if errors:
        return jsonify({"detail": errors}), 422

    base_url = os.getenv('BASE_URL', 'http://localhost:8080')
    full_short_url = f"{base_url.rstrip('/')}/r/{short_name}"

    new_link = db_models.Links(
        original_url=data.get('original_url'),
        short_name=short_name,
        short_url=full_short_url
    )

    with Session(db_engine) as session:
        session.add(new_link)
        session.commit()
        session.refresh(new_link)

    return jsonify(new_link.model_dump()), 201


@app.route('/api/links/<int:id>', methods=['GET'])
def get_link_by_id(id):
    with Session(db_engine) as session:
        link = session.exec(select(db_models.Links)
            .where(db_models.Links.id == id)
            ).first()

    if not link:
        return jsonify({"detail": "Link not found"}), 404

    return jsonify(link.model_dump()), 200


@app.route('/api/links/<int:id>', methods=['PUT'])
def update_link(id):
    data = request.get_json() or {}
    errors = validate(data)

    if errors:
        return jsonify({"detail": errors}), 422

    with Session(db_engine) as session:
        link = session.exec(select(db_models.Links)
            .where(db_models.Links.id == id)
            ).first()
        if not link:
            return jsonify({"detail": "Link not found"}), 404

        link.original_url = data.get('original_url')
        link.short_name = data.get('short_name')

        base_url = os.getenv('BASE_URL', 'http://localhost:8080')
        link.short_url = f"{base_url.rstrip('/')}/r/{data.get('short_name')}"

        session.commit()
        session.refresh(link)
        return jsonify(link.model_dump()), 200


@app.route('/api/links/<int:id>', methods=['DELETE'])
def delete_link(id):
    with Session(db_engine) as session:
        link = session.exec(select(db_models.Links)
            .where(db_models.Links.id == id)
            ).first()
        if not link:
            return jsonify({"detail": "Link not found"}), 404

        session.delete(link)
        session.commit()

    return '', 204


if __name__ == '__main__':
    app.run()
