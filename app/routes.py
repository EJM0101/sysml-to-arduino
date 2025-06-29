from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf.csrf import CSRFError
from app.models.sysml_models import Requirement, Block
from app.models.arduino_generator import ArduinoGenerator
from app import db, csrf

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    requirements = Requirement.query.all()
    blocks = Block.query.all()
    return render_template('diagram_editor.html', 
                         requirements=requirements, 
                         blocks=blocks)

@main_routes.route('/create_requirement', methods=['POST'])
@csrf.exempt  # Temporaire pour debug - À RETIRER après vérification
def create_requirement():
    try:
        # Vérification CSRF (décommenter après test)
        # if not validate_csrf(request.form.get('csrf_token')):
        #     flash('Token de sécurité invalide', 'danger')
        #     return redirect(url_for('main.index'))

        if not all(key in request.form for key in ['name', 'text', 'req_id']):
            flash('Tous les champs sont requis', 'danger')
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
        flash(f'Erreur: {str(e)}', 'danger')
    return redirect(url_for('main.index'))

@main_routes.route('/create_block', methods=['POST'])
def create_block():
    try:
        if not all(field in request.form for field in ['block_name', 'block_type']):
            return jsonify({'error': 'Champs manquants'}), 400

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
        flash(f'Erreur: {str(e)}', 'danger')
        return jsonify({'error': str(e)}), 400
    return redirect(url_for('main.index'))

@main_routes.route('/generate_arduino')
def generate_arduino():
    requirements = Requirement.query.all()
    blocks = Block.query.all()
    arduino_code = ArduinoGenerator.generate_from_models(requirements, blocks)
    return render_template('code_output.html', code=arduino_code)

@main_routes.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('Erreur de sécurité: Token CSRF invalide ou expiré', 'danger')
    return redirect(url_for('main.index'))