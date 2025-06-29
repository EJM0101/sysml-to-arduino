from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.sysml_models import Requirement, Block
from app.models.arduino_generator import ArduinoGenerator
from app import db

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    requirements = Requirement.query.all()
    blocks = Block.query.all()
    return render_template('diagram_editor.html', requirements=requirements, blocks=blocks)

@main_routes.route('/create_requirement', methods=['POST'])
def create_requirement():
    try:
        req = Requirement(
            name=request.form['name'],
            text=request.form['text'],
            req_id=request.form['req_id'],
            parent_id=request.form.get('parent_id') or None
        )
        db.session.add(req)
        db.session.commit()
        flash('Exigence créée avec succès!', 'success')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'danger')
    return redirect(url_for('main.index'))

@main_routes.route('/create_block', methods=['POST'])
def create_block():
    try:
        block = Block(
            name=request.form['name'],
            type=request.form['type'],
            operations=request.form['operations'],
            properties=request.form['properties'],
            constraints=request.form['constraints']
        )
        db.session.add(block)
        db.session.commit()
        flash('Bloc créé avec succès!', 'success')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'danger')
    return redirect(url_for('main.index'))

@main_routes.route('/generate_arduino')
def generate_arduino():
    requirements = Requirement.query.all()
    blocks = Block.query.all()
    arduino_code = ArduinoGenerator.generate_from_models(requirements, blocks)
    return render_template('code_output.html', code=arduino_code)