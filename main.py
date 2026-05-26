from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import engine
from routers import public, admin
from datetime import datetime
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Marta Scarcella Design")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(public.router)
app.include_router(admin.router)

# Globals disponibili in tutti i template
from routers.public import templates as public_templates
from routers.admin import templates as admin_templates

public_templates.env.globals["now"] = datetime.now()
admin_templates.env.globals["now"] = datetime.now()

# Gestione errori
templates_err = Jinja2Templates(directory="templates")

@app.exception_handler(404)
async def not_found(request: Request, exc):
    return templates_err.TemplateResponse(
        request=request,
        name="public/404.html",
        status_code=404,
        context={}
    )

@app.exception_handler(500)
async def server_error(request: Request, exc):
    return templates_err.TemplateResponse(
        request=request,
        name="public/500.html",
        status_code=500,
        context={}
    )