from fastapi import FastAPI

app = FastAPI(title="Smart Plant API")


@app.get("/health")
def health():
    return {"status": "ok"}
