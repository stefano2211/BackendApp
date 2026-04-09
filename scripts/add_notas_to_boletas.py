#!/usr/bin/env python3
"""Script para agregar calificaciones/notas a las boletas existentes."""
import requests
import random
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
        resp = requests.get(f"{BASE_URL}/alumnos?limit=100", headers=headers)
        if resp.status_code == 200:
            alumnos = resp.json()
            filtered = [a for a in alumnos if a.get("grado") == grado and a.get("seccion") == seccion]
            return filtered
    except Exception as e:
        print(f"Error: {e}")
    return []

def get_materias_grado(token, grado, modalidad="Media General"):
    """Obtener materias de un grado específico."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(f"{BASE_URL}/materias?grado={grado}&modalidad={modalidad}&limit=100", headers=headers)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Error: {e}")
    return []

def registrar_nota(token, alumno_id, materia_id, lapso, nota, anio_escolar="2024/2025"):
    """Registrar una nota/calificación."""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "alumno_id": alumno_id,
        "materia_id": materia_id,
        "lapso": lapso,
        "nota": nota,
        "anio_escolar": anio_escolar,
        "literal": get_literal(nota)
    }
    try:
        resp = requests.post(f"{BASE_URL}/calificaciones/", json=data, headers=headers)
        if resp.status_code == 201:
            return resp.json()
        elif resp.status_code == 400:
            # Nota ya existe, intentar actualizar
            return None
        else:
            print(f"❌ Error registrando nota: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    return None

def get_literal(nota):
    """Convertir nota numérica a literal."""
    if nota >= 18:
        return "A"
    elif nota >= 15:
        return "B"
    elif nota >= 12:
        return "C"
    elif nota >= 10:
        return "D"
    else:
        return "E"

def main():
    print("🚀 Agregando calificaciones/notas a las boletas...")
    
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
    
    print(f"✅ {len(alumnos)} alumnos encontrados")
    
    # Get materias for grade 1
    materias = get_materias_grado(token, 1, "Media General")
    if not materias:
        print("❌ No se encontraron materias para 1° grado")
        sys.exit(1)
    
    print(f"✅ {len(materias)} materias encontradas")
    
    # Add grades for each alumno, materia, and lapso
    lapsos = [1, 2, 3]
    notas_registradas = 0
    
    for alumno in alumnos:
        print(f"\n📚 Alumno: {alumno['nombre']} {alumno['apellido']}")
        
        for materia in materias:
            materia_nombre = materia['nombre']
            
            for lapso in lapsos:
                # Generate a random grade between 12 and 19 (passing grades)
                nota = random.randint(12, 19)
                
                result = registrar_nota(token, alumno['id'], materia['id'], lapso, nota)
                if result:
                    notas_registradas += 1
                    print(f"  ✅ {materia_nombre} - Lapso {lapso}: {nota} ({get_literal(nota)})")
    
    print(f"\n✨ {notas_registradas} calificaciones registradas exitosamente!")
    print(f"\n📊 Resumen:")
    print(f"   - Alumnos: {len(alumnos)}")
    print(f"   - Materias: {len(materias)}")
    print(f"   - Lapsos: 1, 2, 3")
    print(f"   - Total notas: {notas_registradas}")
    print(f"\n🎯 Ahora las boletas tendrán notas/calificaciones reales!")

if __name__ == "__main__":
    main()
