from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from core.database import Base


class Nota(Base):
    __tablename__ = "notas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    contenido = Column(String, nullable=True)
    completada = Column(Boolean, default=False)


class Alumno(Base):
    __tablename__ = "alumnos"

    id = Column(Integer, primary_key=True, index=True)
    cedula = Column(String, unique=True, index=True, nullable=False)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    codigo = Column(String, nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    lugar_nacimiento = Column(String, nullable=True)
    estado_nacimiento = Column(String, nullable=True)
    nombre_representante = Column(String, nullable=True)
    direccion_representante = Column(String, nullable=True)

    boletas = relationship("Boleta", back_populates="alumno", cascade="all, delete-orphan")


class Materia(Base):
    __tablename__ = "materias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    grado = Column(Integer, nullable=False, index=True)
    es_numerica = Column(Boolean, default=True)

    calificaciones = relationship("Calificacion", back_populates="materia")


class Boleta(Base):
    __tablename__ = "boletas"

    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False)
    anio_escolar = Column(String, nullable=False)
    grado = Column(Integer, nullable=False)
    seccion = Column(String, nullable=False)
    numero_lista = Column(Integer, nullable=True)
    tipo_evaluacion = Column(String, nullable=False)
    observaciones = Column(String, nullable=True)
    media_lapso_1 = Column(Float, nullable=True)
    media_lapso_2 = Column(Float, nullable=True)
    media_lapso_3 = Column(Float, nullable=True)
    medias_globales = Column(Float, nullable=True)
    profesor = Column(String, nullable=True)
    nombre_plantel = Column(String, nullable=True)
    direccion_plantel = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    alumno = relationship("Alumno", back_populates="boletas")
    calificaciones = relationship("Calificacion", back_populates="boleta", cascade="all, delete-orphan")


class Calificacion(Base):
    __tablename__ = "calificaciones"

    id = Column(Integer, primary_key=True, index=True)
    boleta_id = Column(Integer, ForeignKey("boletas.id"), nullable=False)
    materia_id = Column(Integer, ForeignKey("materias.id"), nullable=False)
    lapso_1_def = Column(Integer, nullable=True)
    lapso_2_def = Column(Integer, nullable=True)
    lapso_3_def = Column(Integer, nullable=True)
    def_final = Column(Integer, nullable=True)
    literal = Column(String, nullable=True)

    boleta = relationship("Boleta", back_populates="calificaciones")
    materia = relationship("Materia", back_populates="calificaciones")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
