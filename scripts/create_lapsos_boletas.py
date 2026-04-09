#!/usr/bin/env python3
"""Script para crear boletas de cada lapso para los alumnos existentes."""
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
    except Exception as e:
        print(f"Error de login: {e}")
    return None

def get_alumnos_seccion(token, grado, seccion):
    """Obtener alumnos de una sección específica."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        # Get all alumnos and filter by grado/seccion
        resp = requests.get(f"{BASE_URL}/alumnos?limit=100", headers=headers)
        if resp.status_code == 200:
            alumnos = resp.json()
            # Filter by grado and seccion
            filtered = [a for a in alumnos if a.get("grado") == grado and a.get("seccion") == seccion]
            return filtered
    except Exception as e:
        print(f"Error: {e}")
    return []

def create_boleta(token, boleta_data):
    """Crear una boleta."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.post(f"{BASE_URL}/boletas/", json=boleta_data, headers=headers)
        if resp.status_code == 201:
            return resp.json()
        elif resp.status_code == 400:
            print(f"⚠️  Boleta ya existe o datos inválidos: {resp.text}")
        else:
            print(f"❌ Error creando boleta: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    return None

def main():
    print("🚀 Creando boletas por lapso...")
    
    token = get_token()
    if not token:
        print("❌ No se pudo obtener token")
        sys.exit(1)
    
    print("✅ Autenticado")
    
    # Get alumnos from section 1-A
    alumnos = get_alumnos_seccion(token, 1, "A")
    if not alumnos:
        print("❌ No se encontraron alumnos en sección 1-A")
        sys.exit(1)
    
    print(f"✅ {len(alumnos)} alumnos encontrados en 1-A")
    
    # Create boletas for each lapso
    lapsos = [
        ("Lapso 1", 1),
        ("Lapso 2", 2),
        ("Lapso 3", 3),
        ("Final", 3)
    ]
    
    boletas_creadas = 0
    
    for alumno in alumnos:
        print(f"\n📄 Creando boletas para {alumno['nombre']} {alumno['apellido']}...")
        
        for tipo_eval, hasta_lapso in lapsos:
            boleta_data = {
                "alumno_id": alumno["id"],
                "anio_escolar": "2024/2025",
                "grado": 1,
                "seccion": "A",
                "modalidad": alumno.get("modalidad", "Media General"),
                "numero_lista": alumno.get("numero_lista", 1),
                "tipo_evaluacion": tipo_eval,
                "hasta_lapso": hasta_lapso,
                "observaciones": f"Evaluación {tipo_eval} - Promovido",
                "profesor": "Prof. García",
                "nombre_plantel": "U.E. Simón Rodríguez",
                "direccion_plantel": "Av. Principal, Caracas"
            }
            
            result = create_boleta(token, boleta_data)
            if result:
                boletas_creadas += 1
                print(f"  ✅ {tipo_eval}")
    
    print(f"\n✨ {boletas_creadas} boletas creadas exitosamente!")
    print(f"\n📊 Resumen por sección 1-A:")
    print(f"   - Alumnos: {len(alumnos)}")
    print(f"   - Lapsos: 1, 2, 3, Final")
    print(f"   - Total boletas: {boletas_creadas}")
    print(f"\n🎯 Ahora puedes descargar:")
    print(f"   - Lapso 1: Todas las boletas del primer lapso")
    print(f"   - Lapso 2: Todas las boletas del segundo lapso")
    print(f"   - Lapso 3: Todas las boletas del tercer lapso")
    print(f"   - Final: Todas las boletas finales")

if __name__ == "__main__":
    main()
