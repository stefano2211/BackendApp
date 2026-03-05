# 🎓 BackendApp API Documentation

## Introducción
Esta es la API del Sistema de Boletas Escolares. Construida con FastAPI y SQLAlchemy. Emplea un sistema de autenticación basado en JWT (JSON Web Tokens) y sigue una arquitectura limpia estructurada en routers, esquemas (Pydantic), servicios y repositorios.

## 🔐 Autenticación Global
Salvo los endpoints bajo el prefijo `/auth` (registro, login, password resets), **todos los demás endpoints están protegidos**. Requieren el envío de un token JWT válido (obtenido al hacer login) en las cabeceras HTTP:
```http
Authorization: Bearer <tu_access_token>
```

---

## 🚀 Endpoints y Payloads

### 1. 🛡️ Autenticación (`/auth`)

#### Registrar Usuario
- **Endpoint:** `POST /auth/register`
- **Descripción:** Crea un nuevo usuario en el sistema. Debe ser único tanto en username como en email.
- **Payload Request:**
```json
{
  "username": "admin",
  "email": "admin@escuela.com",
  "password": "strongpassword123"
}
```

#### Iniciar Sesión (Login)
- **Endpoint:** `POST /auth/login`
- **Descripción:** Ingresa credenciales y retorna el token de acceso JWT.
- **Payload Request:**
```json
{
  "username": "admin",
  "password": "strongpassword123"
}
```
- **Response Esperado:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer"
}
```

#### Solicitar Recuperación de Contraseña
- **Endpoint:** `POST /auth/forgot-password`
- **Payload Request:**
```json
{
  "email": "admin@escuela.com"
}
```

#### Restablecer Contraseña
- **Endpoint:** `POST /auth/reset-password`
- **Payload Request:**
```json
{
  "token": "token_recibido_en_correo",
  "new_password": "nueva_alfa_numerica_321"
}
```

---

### 2. 👨‍🎓 Alumnos (`/alumnos`)

#### Crear Alumno
- **Endpoint:** `POST /alumnos/`
- **Payload Request:** (Los campos opcionales pueden omitirse)
```json
{
  "cedula": "V-12345678",
  "nombre": "Juan",
  "apellido": "Pérez",
  "codigo": "A-001",
  "fecha_nacimiento": "2010-05-14",
  "lugar_nacimiento": "Caracas",
  "estado_nacimiento": "Distrito Capital",
  "nombre_representante": "María de Pérez",
  "direccion_representante": "Av. Principal, Edificio 1"
}
```

#### Obtener Listado de Alumnos
- **Endpoint:** `GET /alumnos/?skip=0&limit=100`

#### Obtener Alumno Específico
- **Por Base ID:** `GET /alumnos/{alumno_id}`
- **Por Cédula:** `GET /alumnos/cedula/{cedula}`

#### Actualizar / Eliminar Alumno
- **Actualizar:** `PUT /alumnos/{alumno_id}` (Se envía JSON similar al de creación, todos los campos son opcionales)
- **Eliminar:** `DELETE /alumnos/{alumno_id}`

---

### 3. 📚 Materias (`/materias`)

#### Crear Materia
- **Endpoint:** `POST /materias/`
- **Payload Request:**
```json
{
  "nombre": "Matemáticas",
  "grado": 3,
  "es_numerica": true
}
```

#### Obtener Materias
- **Endpoint:** `GET /materias/?grado=3&skip=0&limit=100`
- **Filtro útil:** Se puede agregar el Query Param `grado` para obtener únicamente las materias de un grado específico.

#### Actualizar / Eliminar Materia
- **Actualizar:** `PUT /materias/{materia_id}`
- **Eliminar:** `DELETE /materias/{materia_id}`

---

### 4. 📝 Notas Generales / Tareas (`/notas`)
*Nota: Este modelo representa un listado de notas descriptivas, estilo To-Do o recordatorios, no son calificaciones de materias.*

#### Crear Nota
- **Endpoint:** `POST /notas/`
- **Payload Request:**
```json
{
  "titulo": "Revisar expedientes",
  "contenido": "Reunir los documentos faltantes de tercer año.",
  "completada": false
}
```

#### Operaciones Básicas Notas
- **Listar:** `GET /notas/`
- **Ver:** `GET /notas/{nota_id}`
- **Actualizar:** `PUT /notas/{nota_id}`
- **Eliminar:** `DELETE /notas/{nota_id}`

---

### 5. 📄 Boletas y Calificaciones Oficiales (`/boletas`)
El punto principal del negocio donde convergen Alumnos, Materias y Notas (Calificaciones).

#### Crear Boleta de un Alumno
- **Endpoint:** `POST /boletas/`
- **Descripción:** Inserta una estructura compleja. Crea el reporte base (Boleta) para un estudiante y en el mismo pedido adosa la lista de notas de las materias evaluadas que conforman esa boleta (`calificaciones`).
- **Payload Request Completo:**
```json
{
  "alumno_id": 1,
  "anio_escolar": "2023-2024",
  "grado": 3,
  "seccion": "A",
  "numero_lista": 15,
  "tipo_evaluacion": "Final",
  "observaciones": "Excelente rendimiento académico durante el año.",
  "medias_globales": 18.5,
  "profesor": "Lic. Carlos Ruiz",
  "nombre_plantel": "UE Colegio Modelo",
  "direccion_plantel": "Calle 1, Zona Centro",
  "calificaciones": [
    {
      "materia_id": 1,
      "lapso_1_def": 18,
      "lapso_2_def": 19,
      "lapso_3_def": 20,
      "def_final": 19,
      "literal": "A"
    },
    {
      "materia_id": 2,
      "lapso_1_def": 15,
      "lapso_2_def": 16,
      "lapso_3_def": 16,
      "def_final": 16,
      "literal": "B"
    }
  ]
}
```

#### Obtener Boletas (Búsqueda Avanzada)
- **Endpoint:** `GET /boletas/`
- **Query Params de Filtrado Disponibles:** 
  - `?alumno_id=1` (Útil para traer todas las boletas de un mismo estudiante)
  - `&anio_escolar=2023-2024`
  - `&tipo_evaluacion=Final`

#### Obtener Boleta en Detalle
- **Endpoint:** `GET /boletas/{boleta_id}`
- **Retorno:** Devuelve el JSON expansivo de la boleta, auto-poblando el objeto del `Alumno` y detallando la lista de `Calificaciones` con sus materias.

#### Descargar Boleta en PDF 🖨️ (¡Endpoint Especial!)
- **Endpoint:** `GET /boletas/{boleta_id}/pdf`
- **Descripción:** Este endpoint **no retorna JSON**. Transforma los datos de la boleta mediante el servicio `Generador de PDF` y hace stream del contenido del archivo directamente, retornando una cabecera de descarga (`application/pdf`) haciendo que tu navegador descargue el archivo.
- **Formato del archivo autogenerado:** `boleta_{cedula}_{tipo_evaluacion}.pdf`

#### Actualizar o Eliminar Boleta
- **Actualizar:** `PUT /boletas/{boleta_id}`
- **Eliminar:** `DELETE /boletas/{boleta_id}`
