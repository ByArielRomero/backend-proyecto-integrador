from flask import Blueprint, jsonify, request
from models import db, Imputado

imputados_bp = Blueprint('imputados_bp', __name__, url_prefix='/imputados')

@imputados_bp.route('/', methods=['GET'])
def get_all_imputados():
    imputados = Imputado.query.all()
    return jsonify([imputado.to_dict() for imputado in imputados])

@imputados_bp.route('/<int:id_imputado>', methods=['GET'])
def get_imputado(id_imputado):
    imputado = Imputado.query.get_or_404(id_imputado)
    return jsonify(imputado.to_dict())

@imputados_bp.route('/', methods=['POST'])
def create_imputado():
    try:
        data = request.get_json()

        campos_obligatorios = ['nombre', 'dni', 'direccion', 'comisaria', 'jurisdiccion']
        campos_faltantes = [campo for campo in campos_obligatorios if not data or campo not in data or not data[campo]]
        
        if campos_faltantes:
            return jsonify({
                'error': f'Los siguientes campos son obligatorios: {", ".join(campos_faltantes)}'
            }), 400
        
        nombre_normalizado = data['nombre'].strip().lower()
        
        imputado_existente = Imputado.query.filter(
            db.func.lower(Imputado.nombre) == nombre_normalizado
        ).first()
        if imputado_existente:
            return jsonify({'error': f'Ya existe un imputado con el nombre "{imputado_existente.nombre}"'}), 400
        
        nuevo_imputado = Imputado(
            nombre=nombre_normalizado,
            dni=data['dni'],    
            direccion=data['direccion'],
            comisaria=data['comisaria'],
            jurisdiccion=data['jurisdiccion']
        )
        db.session.add(nuevo_imputado)
        db.session.commit()
        return jsonify(nuevo_imputado.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@imputados_bp.route('/<int:id_imputado>', methods=['PATCH'])
def update_imputado(id_imputado):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Se requiere al menos un campo para actualizar'}), 400
        
        imputado = Imputado.query.get_or_404(id_imputado)
        
        if 'nombre' in data:
            if not data['nombre']:
                return jsonify({'error': 'El nombre no puede estar vacío'}), 400
            
            nombre_normalizado = data['nombre'].strip().lower()
            imputado_existente = Imputado.query.filter(
                db.func.lower(Imputado.nombre) == nombre_normalizado,
                Imputado.id != id_imputado 
            ).first()
            if imputado_existente:
                return jsonify({'error': f'Ya existe un imputado con el nombre "{imputado_existente.nombre}"'}), 400
            
            imputado.nombre = data['nombre']
        
        if 'dni' in data:
            imputado.dni = data['dni']
        if 'direccion' in data:
            imputado.direccion = data['direccion']
        if 'comisaria' in data:
            imputado.comisaria = data['comisaria']
        if 'jurisdiccion' in data:
            imputado.jurisdiccion = data['jurisdiccion']
        
        db.session.commit()
        return jsonify(imputado.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

@imputados_bp.route('/<int:id_imputado>', methods=['DELETE'])
def delete_imputado(id_imputado):
    try:
        imputado = Imputado.query.get_or_404(id_imputado)
        db.session.delete(imputado)
        db.session.commit()
        return jsonify({'message': 'Imputado eliminado correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    