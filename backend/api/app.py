from __future__ import annotations

from fastapi import FastAPI


app = FastAPI(title="SVP Backend API (Scaffold)")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}

