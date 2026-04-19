from fastapi import FastAPI

from sdlc_demo.webhook import router as webhook_router

app = FastAPI(title="SDLC Demo")
app.include_router(webhook_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
