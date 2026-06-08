from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes.actions import router as actions_router
import backend.scheduler as scheduler
from backend.agents.action_agent import ActionAgent


@asynccontextmanager
async def lifespan(app: FastAPI):
    ActionAgent().start_poll_loop()
    scheduler.start()
    yield
    scheduler.stop()


app = FastAPI(title="Smart Plant API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(actions_router)


@app.get("/health")
def health():
    return {"status": "ok"}
