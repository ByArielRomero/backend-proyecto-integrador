from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .calzado import Calzado
from .suela import Suela
from .cuadrante import Cuadrante
from .forma_geometrica import FormaGeometrica
from .detalle_suela import DetalleSuela
from .usuario import Usuario
from .color import Color
from .marca import Marca
from .categoria import Categoria
from .modelo import Modelo
from .imputado import Imputado
