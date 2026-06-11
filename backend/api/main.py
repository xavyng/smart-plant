import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes.actions import router as actions_router
from backend.api.routes.sensors import router as sensors_router
from backend.api.routes.pipeline import router as pipeline_router
import backend.scheduler as scheduler
from backend.agents.action_agent import ActionAgent

_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
_ALLOWED_ORIGINS = [o.strip() for o in _raw.split(",") if o.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    ActionAgent().start_poll_loop()
    scheduler.start()
    yield
    scheduler.stop()


app = FastAPI(title="Smart Plant API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(actions_router)
app.include_router(sensors_router)
app.include_router(pipeline_router)


@app.get("/health")
def health():
    return {"status": "ok"}
