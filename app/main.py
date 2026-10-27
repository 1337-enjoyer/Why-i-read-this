from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import wiki
from app.api.routes.auth import include_auth_routers

app = FastAPI(title="WhyIReadThis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wiki.router)
include_auth_routers(app)


@app.get("/health")
async def health():
    return {"status": "ok"}
