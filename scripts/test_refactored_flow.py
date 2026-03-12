
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_decoupled_flow():
    print("--- Probando Flujo Refactorizado: Calificaciones -> Boleta ---")
    
    # 1. Login
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin_test", "password": "password123"})
    if login_resp.status_code != 200:
        # Re-registrar si se perdió la DB
        requests.post(f"{BASE_URL}/auth/register", json={"username": "admin_test", "email": "admin@test.com", "password": "password123"})
        login_resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin_test", "password": "password123"})
    
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Crear Alumno
    unique_id = int(time.time())
    alumno = requests.post(f"{BASE_URL}/alumnos/", json={
        "cedula": f"V-{unique_id}",
        "nombre": "Estudiante",
        "apellido": "Refactorizado"
    }, headers=headers).json()
    alumno_id = alumno["id"]

    # 3. Crear Materia
    materia = requests.post(f"{BASE_URL}/materias/", json={
        "nombre": "Historia",
        "grado": 1
    }, headers=headers).json()
    materia_id = materia["id"]

    # 4. REGISTRAR CALIFICACIÓN (Independiente)
    print("\n[PASO 4] Registrando calificación independiente...")
    calif_data = {
        "alumno_id": alumno_id,
        "materia_id": materia_id,
        "anio_escolar": "2024-2025",
        "lapso_1_def": 15,
        "lapso_2_def": 17
    }
    calif_resp = requests.post(f"{BASE_URL}/calificaciones/", json=calif_data, headers=headers)
    if calif_resp.status_code == 201:
        print(f"✅ Calificación registrada: {calif_resp.json()}")
    else:
        print(f"❌ Error al registrar calificación: {calif_resp.text}")
        return

    # 5. GENERAR BOLETA (Sin enviar las notas en el JSON)
    print("\n[PASO 5] Generando boleta (el sistema debe buscar las notas solo)...")
    boleta_data = {
        "alumno_id": alumno_id,
        "anio_escolar": "2024-2025",
        "grado": 1,
        "seccion": "B",
        "tipo_evaluacion": "Primer Lapso",
        "profesor": "Prof. Refactor",
        "nombre_plantel": "Colegio Logic"
    }
    boleta_resp = requests.post(f"{BASE_URL}/boletas/", json=boleta_data, headers=headers)
    if boleta_resp.status_code == 201:
        boleta = boleta_resp.json()
        print(f"✅ Boleta generada. ID: {boleta['id']}")
        print(f"   - Promedio Calculado: {boleta['medias_globales']}")
        
        # Verificar que el promedio sea (15+17)/2 = 16 
        if boleta['medias_globales'] == 16.0:
            print("   🌟 ÉXITO: El sistema encontró la nota y calculó el promedio correctamente.")
        else:
            print(f"   ⚠️ ADVERTENCIA: Promedio esperado 16.0, se obtuvo {boleta['medias_globales']}")
    else:
        print(f"❌ Error al generar boleta: {boleta_resp.text}")

    # 6. Generar PDF
    pdf_resp = requests.get(f"{BASE_URL}/boletas/{boleta['id']}/pdf", headers=headers)
    if pdf_resp.status_code == 200:
        with open("boleta_refactorizada.pdf", "wb") as f:
            f.write(pdf_resp.content)
        print("\n✅ PDF generado: boleta_refactorizada.pdf")

if __name__ == "__main__":
    test_decoupled_flow()
