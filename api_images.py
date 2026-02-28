from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional
import httpx
import io
import os
import random

app = FastAPI(
    title="API Images IA",
    description="Generation d'images gratuite via Pollinations.ai - Alternative DALL-E",
    version="2.0.0"
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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "image/png,image/*,*/*",
    "Referer": "https://pollinations.ai/"
}

@app.get("/")
def home():
    return {
        "message": "API Images IA - Powered by Pollinations.ai",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "/generate": "Generer une image (?prompt=...&width=1024&height=1024&seed=...)",
            "/url": "Obtenir l'URL directe de l'image (?prompt=...)"
        },
        "exemples": [
            "/generate?prompt=un chat astronaute dans l espace",
            "/generate?prompt=coucher de soleil sur la mer&width=1280&height=720",
            "/url?prompt=portrait futuriste&seed=42"
        ]
    }

@app.get("/url")
def get_image_url(
    prompt: str = Query(..., description="Description de l'image"),
    width: int = Query(1024, ge=256, le=2048),
    height: int = Query(1024, ge=256, le=2048),
    seed: Optional[int] = Query(None)
):
    """
    Retourne l'URL directe de l'image generee (sans telecharger l'image).
    Utile pour afficher directement dans un navigateur ou une application.
    """
    if seed is None:
        seed = random.randint(1, 999999)
    safe_prompt = prompt.replace(" ", "%20")
    url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width={width}&height={height}&seed={seed}&nologo=true"
    return {
        "url": url,
        "prompt": prompt,
        "width": width,
        "height": height,
        "seed": seed
    }

@app.get("/generate")
async def generate_image(
    prompt: str = Query(..., description="Description de l'image a generer"),
    width: int = Query(1024, ge=256, le=2048, description="Largeur en pixels"),
    height: int = Query(1024, ge=256, le=2048, description="Hauteur en pixels"),
    seed: Optional[int] = Query(None, description="Graine aleatoire (pour reproduire une image)")
):
    """
    Genere et retourne une image IA directement en PNG.
    Utilise Pollinations.ai comme moteur de generation gratuit.
    """
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt requis")

    if seed is None:
        seed = random.randint(1, 999999)

    safe_prompt = prompt.replace(" ", "%20")
    url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width={width}&height={height}&seed={seed}&nologo=true"

    try:
        async with httpx.AsyncClient(
            timeout=90.0,
            follow_redirects=True,
            headers=HEADERS
        ) as client:
            response = await client.get(url)

            if response.status_code == 200 and len(response.content) > 1000:
                return StreamingResponse(
                    io.BytesIO(response.content),
                    media_type="image/png",
                    headers={
                        "Content-Disposition": f"inline; filename=image_{seed}.png",
                        "X-Prompt": prompt[:100],
                        "X-Seed": str(seed),
                        "X-Width": str(width),
                        "X-Height": str(height)
                    }
                )
            else:
                raise HTTPException(
                    status_code=503,
                    detail=f"Pollinations.ai indisponible (HTTP {response.status_code}). Essayez /url pour obtenir le lien direct."
                )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Timeout: la generation d'image prend trop de temps. Essayez /url pour le lien direct."
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Erreur: {str(e)}")


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
