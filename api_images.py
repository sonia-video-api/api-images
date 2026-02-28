from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import httpx
import io
import os
import random

app = FastAPI(
    title="API Images IA",
    description="Generation d'images gratuite - Alternative DALL-E",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageRequest(BaseModel):
    prompt: str
    width: int = 1024
    height: int = 1024
    seed: Optional[int] = None

@app.get("/")
def home():
    return {
        "message": "API Images IA",
        "docs": "/docs",
        "generate": "/generate?prompt=un chat astronaute",
        "exemples": [
            "/generate?prompt=un chat astronaute",
            "/generate?prompt=coucher de soleil sur la mer&width=1280&height=720",
            "/generate?prompt=portrait futuriste&seed=42"
        ]
    }

@app.get("/generate")
async def generate_image(
    prompt: str = Query(..., description="Description de l'image a generer"),
    width: int = Query(1024, ge=256, le=2048, description="Largeur en pixels"),
    height: int = Query(1024, ge=256, le=2048, description="Hauteur en pixels"),
    seed: Optional[int] = Query(None, description="Graine aleatoire (pour reproduire une image)")
):
    """
    Genere une image IA a partir d'un texte descriptif (prompt).
    Utilise Pollinations.ai comme moteur de generation gratuit.
    """
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt requis")

    if seed is None:
        seed = random.randint(1, 999999)

    safe_prompt = prompt.replace(" ", "%20")
    url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width={width}&height={height}&seed={seed}&nologo=true"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url)

            if response.status_code == 200:
                return StreamingResponse(
                    io.BytesIO(response.content),
                    media_type="image/png",
                    headers={
                        "Content-Disposition": f"inline; filename=image_{seed}.png",
                        "X-Prompt": prompt[:50],
                        "X-Seed": str(seed)
                    }
                )
            else:
                raise HTTPException(status_code=500, detail="Erreur generation image")

    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service indisponible: {str(e)}")


@app.post("/generate")
async def generate_image_post(request: ImageRequest):
    """
    Genere une image via une requete POST avec un corps JSON.
    """
    return await generate_image(
        prompt=request.prompt,
        width=request.width,
        height=request.height,
        seed=request.seed
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
