from . import db

class Imputado(db.Model):
    __tablename__ = 'Imputado'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    dni = db.Column(db.Integer, nullable=False)
    direccion = db.Column(db.String(100), nullable=False)
    comisaria = db.Column(db.String(100), nullable=False)
    jurisdiccion = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'dni': self.dni,
            'direccion': self.direccion,
            'comisaria': self.comisaria,
            'jurisdiccion': self.jurisdiccion
        }