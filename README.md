# API Images IA

API de génération d'images IA gratuite, basée sur [Pollinations.ai](https://pollinations.ai).
Alternative gratuite à DALL-E, déployée sur Render.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Page d'accueil |
| `GET /generate?prompt=...` | Générer une image |
| `POST /generate` | Générer une image (JSON) |
| `GET /docs` | Documentation interactive |

## Exemples

```bash
# Image simple
curl "https://api-images-ia.onrender.com/generate?prompt=un chat astronaute" --output image.png

# Image avec dimensions personnalisées
curl "https://api-images-ia.onrender.com/generate?prompt=coucher de soleil&width=1280&height=720" --output image.png
```

## Déploiement

Déployé sur [Render](https://render.com) — plan gratuit.
