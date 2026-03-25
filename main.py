# backend/app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.app.API import Analyzer_rout as Analyzer_routes
from backend.app.model.forensics_db import init_db
import os

app = FastAPI(title="Memory Analyzer Web")


@app.on_event("startup")
def on_startup():
    init_db()


# ─────────────────────────────────────────
# صفحات HTML  ← مسارات مستقلة لا تتعارض مع الـ API
# ─────────────────────────────────────────

@app.get("/", response_class=FileResponse)
def serve_index():
    return FileResponse(os.path.join("frontend", "AnalyzerPage.html"))


# /result/{id}  →  HTML page
# /analyzer/result/{id}  →  API JSON  (معرّف في الـ router)
@app.get("/result/{analysis_id}", response_class=FileResponse)
def serve_result_page(analysis_id: int):
    return FileResponse(os.path.join("frontend", "AnalyzerResultPage.html"))


# ─────────────────────────────────────────
# API Routes
# ─────────────────────────────────────────
app.include_router(Analyzer_routes.router)   # /analyzer/*  ← JSON files

# ─────────────────────────────────────────
# Static Files
# ─────────────────────────────────────────
app.mount("/static", StaticFiles(directory="frontend"), name="static")