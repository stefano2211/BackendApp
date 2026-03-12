import uvicorn
import sys
import os
from main import app

# Ensure the current directory is in the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Iniciando Servidor de Boletas Escolares...")
    print("Accede a: http://localhost:8000/docs")
    
    # Run the uvicorn server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")
