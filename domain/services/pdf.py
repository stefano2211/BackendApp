import os
from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
from domain.schemas.boleta import BoletaResponse


class PDFService:
    def __init__(self):
        # Configurar Jinja2 para cargar plantillas desde domain/templates
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def generar_boleta_pdf(self, boleta: BoletaResponse) -> BytesIO:
        """
        Genera un PDF a partir de una boleta y lo devuelve como un objeto BytesIO.
        """
        # 1. Cargar plantilla
        template = self.jinja_env.get_template("boleta_pdf.html")

        # 2. Renderizar HTML con los datos
        html_content = template.render(boleta=boleta)

        # 3. Crear buffer en memoria para el PDF
        pdf_buffer = BytesIO()

        # 4. Convertir HTML a PDF
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

        if pisa_status.err:
            raise Exception("Error al generar el PDF")

        # 5. Volver al inicio del buffer para que pueda ser leído
        pdf_buffer.seek(0)
        return pdf_buffer
