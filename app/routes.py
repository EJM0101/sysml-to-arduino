from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf.csrf import CSRFError
from app.models.sysml_models import Requirement, Block
from app.models.arduino_generator import ArduinoGenerator
from app import db, csrf

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    requirements = Requirement.query.order_by(Requirement.req_id).all()
    blocks = Block.query.order_by(Block.name).all()
    return render_template('diagram_editor.html',
                        requirements=requirements,
                        blocks=blocks)

@main_routes.route('/create_requirement', methods=['POST'])
def create_requirement():
    try:
        if not all(key in request.form for key in ['name', 'text', 'req_id']):
            flash('Tous les champs obligatoires doivent être remplis', 'danger')
            return redirect(url_for('main.index'))

        req = Requirement(
            name=request.form['name'],
            text=request.form['text'],
            req_id=request.form['req_id'],
            parent_id=request.form.get('parent_id')
        )
        db.session.add(req)
        db.session.commit()
        flash('Exigence créée avec succès!', 'success')
    except Exception as e:
        flash(f'Erreur lors de la création: {str(e)}', 'danger')
    return redirect(url_for('main.index'))

@main_routes.route('/create_block', methods=['POST'])
def create_block():
    try:
        if not all(field in request.form for field in ['block_name', 'block_type']):
            flash('Les champs Nom et Type sont obligatoires', 'danger')
            return redirect(url_for('main.index'))

        block = Block(
            name=request.form['block_name'],
            type=request.form['block_type'],
            properties=request.form.get('properties', ''),
            operations=request.form.get('operations', ''),
            constraints=request.form.get('constraints', '')
        )
        db.session.add(block)
        db.session.commit()
        flash('Bloc créé avec succès!', 'success')
    except Exception as e:
        flash(f'Erreur lors de la création: {str(e)}', 'danger')
    return redirect(url_for('main.index'))

@main_routes.route('/generate_arduino')
def generate_arduino():
    try:
        requirements = Requirement.query.all()
        blocks = Block.query.all()
        
        if not requirements or not blocks:
            flash('Créez au moins une exigence et un bloc avant de générer le code', 'warning')
            return redirect(url_for('main.index'))

        arduino_code = ArduinoGenerator.generate_from_models(requirements, blocks)
        return render_template('code_output.html', code=arduino_code)
    except Exception as e:
        flash(f'Erreur lors de la génération: {str(e)}', 'danger')
        return redirect(url_for('main.index'))

@main_routes.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('Erreur de sécurité: Veuillez rafraîchir la page et réessayer', 'danger')
    return redirect(url_for('main.index'))