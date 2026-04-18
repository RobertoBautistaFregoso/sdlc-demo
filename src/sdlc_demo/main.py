from fastapi import FastAPI

app = FastAPI(title="SDLC Demo")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/webhook")
def webhook() -> dict:
    return {}
