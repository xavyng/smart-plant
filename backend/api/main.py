from fastapi import FastAPI
from backend.api.routes.actions import router as actions_router

app = FastAPI(title="Smart Plant API")
app.include_router(actions_router)


@app.get("/health")
def health():
    return {"status": "ok"}
