import os
from ast import literal_eval

from flask import Blueprint, jsonify, make_response, redirect, request

from ..database import db_models
from . import db_access as db
from .validator import validate

api_bp = Blueprint('api', __name__)

@api_bp.get('/ping')
def ping_pong():
    return 'pong', 200

@api_bp.route('/api/links')
def get_links():
    range_str = request.args.get('range')

    if not range_str:
        links = db.get_links_by_created_at()


        return jsonify([link.model_dump() for link in links]), 200

    try:
        parsed_range = literal_eval(range_str)
        start = int(parsed_range[0])
        end = int(parsed_range[1])
    except (ValueError, SyntaxError, IndexError, TypeError):
        start, end = 0, 10

    limit_count = end - start

    links, total_links = db.get_links_with_pagination(start, limit_count)

    links_list = [link.model_dump() for link in links]

    response = make_response(jsonify(links_list))
    response.headers['Content-Range'] = f"links {start}-{end}/{total_links}"
    response.headers['Content-Type'] = 'application/json'
    return response, 200


@api_bp.post('/api/links')
def create_link():
    data = request.get_json() or {}
    errors = validate(data)

    short_name = data.get('short_name')

    name_existing = db.get_short_name_if_exists(short_name)

    if name_existing:
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

    db.db_write('create', new_link)

    return jsonify(new_link.model_dump()), 201


@api_bp.route('/api/links/<int:id>')
def get_link_by_id(id):
    link = db.get_link_by_id(id)

    if not link:
        return jsonify({"detail": "Link not found"}), 404

    return jsonify(link.model_dump()), 200


@api_bp.route('/api/links/<int:id>', methods=['PUT'])
def update_link(id):
    data = request.get_json() or {}
    errors = validate(data)

    if errors:
        return jsonify({"detail": errors}), 422

    link = db.get_link_by_id(id)

    if not link:
        return jsonify({"detail": "Link not found"}), 404

    link.original_url = data.get('original_url')
    link.short_name = data.get('short_name')

    base_url = os.getenv('BASE_URL', 'http://localhost:8080')
    link.short_url = f"{base_url.rstrip('/')}/r/{data.get('short_name')}"

    db.db_write('get', link)

    return jsonify(link.model_dump()), 200


@api_bp.route('/api/links/<int:id>', methods=['DELETE'])
def delete_link(id):

    link = db.get_link_by_id(id)

    if not link:
        return jsonify({"detail": "Link not found"}), 404

    db.db_write('delete', link)

    return '', 204


@api_bp.route('/api/links/<short_name>')
def redirect_to_original(short_name):
    link = db.get_short_name_if_exists(short_name)

    if not link:
        return jsonify({"detail": "Link not found"}), 404

    return redirect(link.original_url)
