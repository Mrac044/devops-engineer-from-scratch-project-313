import os

from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlmodel import Session, select
from ast import literal_eval

from ..database import create_db_and_tables, db_engine, db_models
from .validator import validate

create_db_and_tables()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

@app.route('/')
def start_page():
    return render_template('index.html')

@app.route('/api/links')
def get_links():
    range_str = request.args.get('range')
    
    if not range_str:
        with Session(db_engine) as session:
            links = session.exec(select(db_models.Links).order_by(db_models.Links.created_at)).all()

        messages = get_flashed_messages(with_categories=True)
        links_list = [link.model_dump() for link in links]
        return render_template('links_list.html', links=links_list, messages=messages)
    
    parsed_range = literal_eval(range_str)
    
    with Session(db_engine) as session:
        links = session.exec(
            select(db_models.Links)
            .order_by(db_models.Links.created_at)
            .offset(parsed_range[0])
            .limit(parsed_range[1] - parsed_range[0])
        ).all()
        
    messages = get_flashed_messages(with_categories=True)
    links_list = [link.model_dump() for link in links]

    return render_template('links_list.html', links=links_list, messages=messages)

@app.route('/api/links/new')
def add_link():
    return render_template('form_add.html', link={}, errors={})

@app.post('/api/links')
def links_link():
    data = request.form.to_dict()
    errors = validate(data)
    with Session(db_engine) as session:
        if session.exec(select(db_models.Links).where(db_models.Links.short_name == data.get('short_name'))).first():
            errors['unique_name'] = "This name already exists"
    if errors:
        return render_template(
            'form_add.html',
            link=data,
            errors=errors
        ), 422
    base_url = os.getenv('BASE_URL', 'http://localhost:8080')
    full_short_url = f"{base_url.rstrip('/')}/{data.get('short_name')}"
    new_link = db_models.Links(
        original_url=data.get('original_url'),
        short_name=data.get('short_name'),
        short_url=full_short_url
    )

    with Session(db_engine) as session:
        session.add(new_link)
        session.commit()
        session.refresh(new_link)
    flash('Link has been created', 'success')
    return redirect(url_for('get_links'))

@app.route('/api/links/<int:id>')
def link_index(id):
    with Session(db_engine) as session:
        link = session.exec(select(db_models.Links).where(db_models.Links.id == id)).first()
    if not link:
        return "Not found", 404
    link = link.model_dump()
    return render_template('link_index.html', link=link)

@app.route('/api/links/<int:id>/update')
def link_edit(id):
    with Session(db_engine) as session:
        link = session.exec(select(db_models.Links).where(db_models.Links.id == id)).first()
    if not link:
        return "Not found", 404
    link_dict = link.model_dump()
    return render_template('form_edit.html', link=link_dict, errors={})

@app.post('/api/links/<int:id>/update')
def link_patch(id):
    data = request.form.to_dict()
    errors = validate(data)
    if errors:
        data['id'] = id
        return render_template(
            'form_edit.html',
            link=data,
            errors=errors
        ), 422

    with Session(db_engine) as session:
        link = session.exec(select(db_models.Links).where(db_models.Links.id == id)).first()
        if not link:
            return "Link not found", 404

        link.original_url = data.get('original_url')
        link.short_name = data.get('short_name')

        base_url = os.getenv('BASE_URL', 'http://localhost:8080')
        link.short_url = f"{base_url.rstrip('/')}/{data.get('short_name')}"

        session.commit()
        session.refresh(link)

    flash('Link has been updated', 'success')
    return redirect(url_for('get_links'))

@app.route('/api/links/<int:id>/delete_confirm')
def link_delete_confirm(id):
    with Session(db_engine) as session:
            link = session.exec(select(db_models.Links).where(db_models.Links.id == id)).first()
            if not link:
                return "Not found", 404

    delete_url = url_for('link_delete', id=id)

    flash_message = f"Are you sure you want to delete '{link.short_name}'? <a href='{delete_url}' >YES, DELETE</a>"
    flash(flash_message, "warning")
    return redirect(url_for('get_links'))

@app.route('/api/links/<int:id>/delete')
def link_delete(id):
    with Session(db_engine) as session:
        link = session.exec(select(db_models.Links).where(db_models.Links.id == id)).first()
        if not link:
            return "Not found", 404
        session.delete(link)
        session.commit()

    flash('Link has been deleted', 'success')
    return redirect(url_for('get_links'))


if __name__ == '__main__':
    app.run()

