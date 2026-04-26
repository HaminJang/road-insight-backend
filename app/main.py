from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from datetime import datetime, timezone
from typing import Optional
from app.schemas import AnalysisResponse, DamageDetection
from app.analyzer import analyze_image
from app.hasher import generate_hash
from app.pdf_generator import generate_evidence_pdf

app = FastAPI(title="Road-Insight API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Road-Insight API 정상 작동 중"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    file: UploadFile = File(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None)
):
    image_bytes = await file.read()
    hash_value = generate_hash(image_bytes)
    timestamp = datetime.now(timezone.utc).isoformat()
    result = analyze_image(image_bytes)

    return AnalysisResponse(
        success=True,
        hash=hash_value,
        timestamp=timestamp,
        latitude=latitude,
        longitude=longitude,
        detection=DamageDetection(
            detected=result["detected"],
            confidence=result["confidence"],
            area_ratio=result["area_ratio"],
            damage_score=result["damage_score"],
            bbox=result["bbox"]
        ),
        message=result["message"]
    )

@app.post("/generate-pdf")
async def generate_pdf(
    file: UploadFile = File(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None)
):
    image_bytes = await file.read()
    hash_value = generate_hash(image_bytes)
    timestamp = datetime.now(timezone.utc).isoformat()
    result = analyze_image(image_bytes)

    pdf_bytes = generate_evidence_pdf(
        image_bytes=image_bytes,
        hash_value=hash_value,
        timestamp=timestamp,
        latitude=latitude,
        longitude=longitude,
        confidence=result["confidence"],
        damage_score=result["damage_score"],
        detected=result["detected"]
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=road_insight_{timestamp[:10]}.pdf"
        }
    )
