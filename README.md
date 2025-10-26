# WalloAI Backend (Render-ready)

This repo is prepared for Render automatic deployment. It supports multiple HF models.

Endpoints:
- GET /api/test  => health check
- POST /api/generate (form-data) => prompt (string), model (string, optional), image (file, optional)
- GET /api/images => list generated images
- GET /api/outputs/{filename} => serve image file
