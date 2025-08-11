from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="LINGUAPI Challenge",
    description="Stateless FastAPI CTF for API basics.",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

@app.get("/intro")
def intro():
    return {
        "welcome": "👋 Welcome to the LINGUAPI Challenge!",
        "start": "Begin at /bronze/tasks",
        "hint": "Use the /docs route in your browser to explore available endpoints."
    }

# --- Uncomment when you add bronze router ---
from bronze import router as bronze_router
app.include_router(bronze_router, prefix="/bronze", tags=["Bronze Tier"])
