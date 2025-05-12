from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
import os
import platform

app = FastAPI(title="DMIG Web Server")

# Configuración de directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página principal con información sobre la descarga del agente"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/download/{os_type}")
async def download_agent(os_type: str, arch: str = "x64"):
    """Endpoint para descargar el agente según el sistema operativo y arquitectura"""
    downloads_path = os.path.join(BASE_DIR, "static", "downloads")
    
    if os_type.lower() == "windows":
        if arch.lower() == "x64":
            agent_path = os.path.join(downloads_path, "windows", f"dmig_agent_{arch}.exe")
        else:
            agent_path = os.path.join(downloads_path, "dmig_agent_x86.exe")
    else:
        raise HTTPException(status_code=400, detail="Sistema operativo no soportado")

    if not os.path.exists(agent_path):
        raise HTTPException(
            status_code=404, 
            detail=f"Archivo no encontrado: {os.path.basename(agent_path)}"
        )

    return FileResponse(
        agent_path,
        media_type="application/octet-stream",
        filename=os.path.basename(agent_path)
    )

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado del servidor"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
