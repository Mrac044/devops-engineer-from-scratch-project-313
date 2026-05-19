import os

from flask import Flask, request, render_template, redirect, url_for, flash
from sqlmodel import Session, select
from ..database import db_engine, create_db_and_tables, db_models

with create_db_and_tables():
    pass

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
app.config['BASE_URL'] = os.getenv('BASE_URL', 'http://localhost:8080')


def get_link_or_404(link_id: int, session: Session):
    return session.get(db_models.Links, link_id)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/links')
def list_links():
    with Session(db_engine) as session:
        links = session.exec(select(db_models.Links)).all()
        return render_template('links_list.html', links=links, base_url=app.config['BASE_URL'])


@app.route('/links/new', methods=['GET', 'POST'])
def create_link_ui():
    if request.method == 'POST':
        original_url = request.form.get('original_url')
        short_name = request.form.get('short_name')
        if not original_url or not short_name:
            flash('Both fields are required', 'error')
            return render_template('link_form.html', link=None), 400

        with Session(db_engine) as session:
            existing = session.exec(
                select(db_models.Links).where(db_models.Links.short_name == short_name)
            ).first()
            if existing:
                flash('Short name already taken', 'error')
                return render_template('link_form.html', link=None), 409

            short_url = f"{app.config['BASE_URL']}/r/{short_name}"
            new_link = db_models.Links(
                original_url=original_url,
                short_name=short_name,
                short_url=short_url
            )
            session.add(new_link)
            session.commit()
        flash('Link created successfully', 'success')
        return redirect(url_for('list_links'))
    return render_template('link_form.html', link=None)


@app.route('/links/<int:link_id>/edit', methods=['GET', 'POST'])
def edit_link_ui(link_id):
    with Session(db_engine) as session:
        link = get_link_or_404(link_id, session)
        if not link:
            flash('Link not found', 'error')
            return redirect(url_for('list_links'))

        if request.method == 'POST':
            original_url = request.form.get('original_url')
            short_name = request.form.get('short_name')
            if not original_url or not short_name:
                flash('Both fields are required', 'error')
                return render_template('link_form.html', link=link), 400

            # Проверка уникальности если short_name изменился
            if short_name != link.short_name:
                existing = session.exec(
                    select(db_models.Links).where(
                        db_models.Links.short_name == short_name,
                        db_models.Links.id != link_id
                    )
                ).first()
                if existing:
                    flash('Short name already taken', 'error')
                    return render_template('link_form.html', link=link), 409
                link.short_name = short_name
                link.short_url = f"{app.config['BASE_URL']}/r/{short_name}"

            link.original_url = original_url
            session.add(link)
            session.commit()
            flash('Link updated successfully', 'success')
            return redirect(url_for('list_links'))

        return render_template('link_form.html', link=link)


@app.route('/links/<int:link_id>/delete', methods=['POST'])
def delete_link_ui(link_id):
    with Session(db_engine) as session:
        link = get_link_or_404(link_id, session)
        if not link:
            flash('Link not found', 'error')
        else:
            session.delete(link)
            session.commit()
            flash('Link deleted successfully', 'success')
    return redirect(url_for('list_links'))


@app.route('/r/<short_name>')
def redirect_to_original(short_name):
    with Session(db_engine) as session:
        link = session.exec(
            select(db_models.Links).where(db_models.Links.short_name == short_name)
        ).first()
        if not link:
            return "Link not found", 404
        return redirect(link.original_url)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)