from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from domain.schemas.boleta import BoletaCreate, BoletaUpdate, BoletaResponse, BoletaListResponse
from domain.services.boleta import BoletaService
from domain.services.pdf import PDFService
from api.deps import get_boleta_service, get_pdf_service

router = APIRouter()


@router.get("/bulk/pdf")
def get_bulk_boletas_pdf(
    grado: int = Query(..., description="Grado de la sección"),
    seccion: str = Query(..., description="Letra de la sección"),
    anio_escolar: str = Query(..., description="Año escolar"),
    tipo_evaluacion: str = Query(..., description="Tipo de evaluación"),
    service: BoletaService = Depends(get_boleta_service),
    pdf_service: PDFService = Depends(get_pdf_service),
):
    print(f"DEBUG: Buscando boletas bulk - Grado: {grado}, Sección: {seccion}, Año: {anio_escolar}, Tipo: {tipo_evaluacion}")
    boletas = service.obtener_boletas_bulk(grado, seccion, anio_escolar, tipo_evaluacion)
    print(f"DEBUG: Se encontraron {len(boletas)} boletas")
    if not boletas:
        # Return empty PDF with message instead of 404
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from io import BytesIO
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica", 12)
        p.drawString(100, 750, f"No se encontraron boletas para:")
        p.drawString(100, 730, f"Grado: {grado}°")
        p.drawString(100, 710, f"Sección: {seccion}")
        p.drawString(100, 690, f"Año Escolar: {anio_escolar}")
        p.drawString(100, 670, f"Tipo Evaluación: {tipo_evaluacion}")
        p.save()
        
        buffer.seek(0)
        pdf_buffer = buffer
    else:
        pdf_buffer = pdf_service.generar_bulk_boletas_pdf(boletas)
    
    filename = f"boletas_{grado}{seccion}_{anio_escolar.replace('/', '-')}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/{boleta_id}/pdf")
def get_boleta_pdf(
    boleta_id: int,
    service: BoletaService = Depends(get_boleta_service),
    pdf_service: PDFService = Depends(get_pdf_service),
):
    boleta = service.obtener_boleta(boleta_id)
    if not boleta:
        raise HTTPException(status_code=404, detail="Boleta no encontrada")
    
    pdf_buffer = pdf_service.generar_boleta_pdf(boleta)
    
    filename = f"boleta_{boleta.alumno.cedula}_{boleta.tipo_evaluacion.replace(' ', '_')}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/", response_model=BoletaResponse, status_code=201)
def create_boleta(
    boleta_in: BoletaCreate,
    service: BoletaService = Depends(get_boleta_service),
) -> BoletaResponse:
    return service.crear_boleta(boleta_in)


@router.get("/", response_model=List[BoletaListResponse])
def read_boletas(
    alumno_id: int | None = Query(None, description="Filtrar por alumno"),
    anio_escolar: str | None = Query(None, description="Filtrar por año escolar (ej: 2024/2025)"),
    tipo_evaluacion: str | None = Query(None, description="Filtrar por tipo de evaluación"),
    skip: int = 0,
    limit: int = 100,
    service: BoletaService = Depends(get_boleta_service),
) -> List[BoletaListResponse]:
    return service.listar_boletas(
        skip=skip,
        limit=limit,
        alumno_id=alumno_id,
        anio_escolar=anio_escolar,
        tipo_evaluacion=tipo_evaluacion,
    )


@router.get("/{boleta_id}", response_model=BoletaResponse)
def read_boleta(
    boleta_id: int,
    service: BoletaService = Depends(get_boleta_service),
) -> BoletaResponse:
    boleta = service.obtener_boleta(boleta_id)
    if not boleta:
        raise HTTPException(status_code=404, detail="Boleta no encontrada")
    return boleta


@router.put("/{boleta_id}", response_model=BoletaResponse)
def update_boleta(
    boleta_id: int,
    boleta_in: BoletaUpdate,
    service: BoletaService = Depends(get_boleta_service),
) -> BoletaResponse:
    boleta = service.actualizar_boleta(boleta_id, boleta_in)
    if not boleta:
        raise HTTPException(status_code=404, detail="Boleta no encontrada")
    return boleta


@router.delete("/{boleta_id}", status_code=204)
def delete_boleta(
    boleta_id: int,
    service: BoletaService = Depends(get_boleta_service),
):
    success = service.eliminar_boleta(boleta_id)
    if not success:
        raise HTTPException(status_code=404, detail="Boleta no encontrada")
