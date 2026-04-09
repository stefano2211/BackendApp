#!/usr/bin/env python3
"""Script para crear alumnos y boletas de prueba rápidamente."""
import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def get_token():
    """Obtener token de autenticación."""
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if resp.status_code == 200:
            return resp.json()["access_token"]
        else:
            print(f"Login failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Error de login: {e}")
    return None

def create_seccion(token, grado, letra, modalidad="Media General"):
    """Crear una sección si no existe."""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "grado": grado,
        "letra": letra,
        "modalidad": modalidad,
        "anio_escolar": "2024/2025"
    }
    try:
        resp = requests.post(f"{BASE_URL}/secciones/", json=data, headers=headers)
        if resp.status_code == 201:
            print(f"✅ Sección {grado}-{letra} ({modalidad}) creada")
            return resp.json()
        elif resp.status_code == 400 and "ya existe" in resp.text:
            print(f"ℹ️ Sección {grado}-{letra} ya existe")
            # Buscar la sección existente
            resp_get = requests.get(f"{BASE_URL}/secciones/", headers=headers)
            if resp_get.status_code == 200:
                for s in resp_get.json():
                    if s["grado"] == grado and s["letra"] == letra and s.get("modalidad") == modalidad:
                        return s
        else:
            print(f"❌ Error creando sección {grado}-{letra}: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    return None

def create_alumno(token, alumno_data):
    """Crear un alumno."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.post(f"{BASE_URL}/alumnos/", json=alumno_data, headers=headers)
        if resp.status_code == 201:
            print(f"✅ Alumno {alumno_data['nombre']} {alumno_data['apellido']} creado")
            return resp.json()
        else:
            print(f"❌ Error creando alumno: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    return None

def create_boleta(token, boleta_data):
    """Crear una boleta."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.post(f"{BASE_URL}/boletas/", json=boleta_data, headers=headers)
        if resp.status_code == 201:
            print(f"✅ Boleta para alumno {boleta_data['alumno_id']} creada")
            return resp.json()
        else:
            print(f"❌ Error creando boleta: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    return None

def main():
    print("🚀 Creando datos de prueba...")
    
    # Obtener token
    token = get_token()
    if not token:
        print("❌ No se pudo obtener token. ¿Está corriendo el backend?")
        sys.exit(1)
    
    print("✅ Autenticado correctamente")
    
    # Crear secciones
    seccion_1a = create_seccion(token, 1, "A", "Media General")
    seccion_1b = create_seccion(token, 1, "B", "Media General")
    
    if not seccion_1a:
        print("❌ No se pudo crear/obtener la sección 1-A")
        sys.exit(1)
    
    # Crear alumnos para sección 1-A
    alumnos_data = [
        {
            "cedula": "V-31000001",
            "nombre": "Juan",
            "apellido": "Pérez",
            "codigo": "AL-001",
            "fecha_nacimiento": "2010-03-15",
            "lugar_nacimiento": "Caracas",
            "estado_nacimiento": "Distrito Capital",
            "municipio": "Libertador",
            "nombre_representante": "María Pérez",
            "telefono_representante": "+58 414-1234567",
            "correo_representante": "maria@test.com",
            "direccion_representante": "Av. Principal, Caracas",
            "correo_estudiante": "juan@test.com",
            "grado": 1,
            "seccion": "A",
            "modalidad": "Media General",
            "numero_lista": 1,
            "status": "presente"
        },
        {
            "cedula": "V-31000002",
            "nombre": "Ana",
            "apellido": "García",
            "codigo": "AL-002",
            "fecha_nacimiento": "2010-05-20",
            "lugar_nacimiento": "Caracas",
            "estado_nacimiento": "Distrito Capital",
            "municipio": "Libertador",
            "nombre_representante": "Pedro García",
            "telefono_representante": "+58 414-7654321",
            "correo_representante": "pedro@test.com",
            "direccion_representante": "Av. Secundaria, Caracas",
            "correo_estudiante": "ana@test.com",
            "grado": 1,
            "seccion": "A",
            "modalidad": "Media General",
            "numero_lista": 2,
            "status": "presente"
        },
        {
            "cedula": "V-31000003",
            "nombre": "Carlos",
            "apellido": "López",
            "codigo": "AL-003",
            "fecha_nacimiento": "2010-07-10",
            "lugar_nacimiento": "Valencia",
            "estado_nacimiento": "Carabobo",
            "municipio": "Valencia",
            "nombre_representante": "Laura López",
            "telefono_representante": "+58 416-9876543",
            "correo_representante": "laura@test.com",
            "direccion_representante": "Av. Bolívar, Valencia",
            "correo_estudiante": "carlos@test.com",
            "grado": 1,
            "seccion": "A",
            "modalidad": "Media General",
            "numero_lista": 3,
            "status": "presente"
        }
    ]
    
    alumnos_creados = []
    for alumno_data in alumnos_data:
        alumno = create_alumno(token, alumno_data)
        if alumno:
            alumnos_creados.append(alumno)
    
    if not alumnos_creados:
        print("❌ No se pudieron crear alumnos")
        sys.exit(1)
    
    print(f"\n✅ {len(alumnos_creados)} alumnos creados")
    
    # Crear boletas para cada alumno
    print("\n📄 Creando boletas...")
    for alumno in alumnos_creados:
        boleta_data = {
            "alumno_id": alumno["id"],
            "anio_escolar": "2024/2025",
            "grado": 1,
            "seccion": "A",
            "modalidad": "Media General",
            "numero_lista": alumno["numero_lista"],
            "tipo_evaluacion": "Parcial L1+L2",
            "hasta_lapso": 2,
            "observaciones": "Promovido satisfactoriamente",
            "profesor": "Prof. García",
            "nombre_plantel": "U.E. 'Simón Rodríguez'",
            "direccion_plantel": "Av. Principal, Caracas"
        }
        create_boleta(token, boleta_data)
    
    print("\n✨ Datos de prueba creados exitosamente!")
    print(f"\n📊 Resumen:")
    print(f"   - Sección: 1° A (Media General)")
    print(f"   - Año Escolar: 2024/2025")
    print(f"   - Tipo Evaluación: Parcial L1+L2")
    print(f"   - Alumnos: {len(alumnos_creados)}")
    print(f"\n🎯 Ahora puedes probar la descarga masiva con:")
    print(f"   Grado: 1, Sección: A, Año: 2024/2025, Tipo: Parcial L1+L2")

if __name__ == "__main__":
    main()
