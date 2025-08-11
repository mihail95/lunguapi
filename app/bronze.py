from fastapi import APIRouter, Query, Path, Header, HTTPException
from pydantic import BaseModel, Field
import re

router = APIRouter()

# ---- Static flags (no hashing) ----
FLAG_HELLO = "BRZ1-HELLO-9f2a"
FLAG_REST  = "BRZ2-REST-1c3d"
FLAG_ECHO  = "BRZ3-ECHO-b7e4"
FLAG_UA    = "BRZ4-UA-5d10"
FLAG_FINAL = "BRZ-FINAL-7abc"

# ---------------------------
# Tasks (concise, non-spoiler)
# ---------------------------
@router.get("/tasks", summary="Bronze: tasks overview")
def tasks():
    return {
        "1. Say Hello": {
            "endpoint": "/bronze/hello",
            "method": "GET",
            "learn": "Query parameters",
            "description": "Introduce yourself to the API.",
            "hint": "Call the route with a single query parameter."
        },
        "2. Find the REST endpoint": {
            "endpoint": "/bronze/discover",
            "method": "GET",
            "learn": "REST resource naming + path parameters",
            "description": "Infer a resource-style path and fetch a specific item.",
            "hint": "Start at /bronze/discover for a clue."
        },
        "3. Body Parameters": {
            "endpoint": "/bronze/echo",
            "method": "POST",
            "learn": "JSON request body",
            "description": "Send a short phrase for the server to process.",
            "hint": "POST a small JSON object."
        },
        "4. Request Headers": {
            "endpoint": "/bronze/client",
            "method": "GET",
            "learn": "HTTP headers (User-Agent)",
            "description": "Identify your client as if scraping politely.",
            "hint": "Send one header that names your client."
        },
        "5. Get the Bronze Flag": {
            "endpoint": "/bronze/final",
            "method": "POST",
            "learn": "Chaining and verification",
            "description": "Combine the four flags to unlock Bronze.",
            "hint": "Submit the four codes in order."
        }
    }

# ---------------------------
# 1) Hello (query parameter)
# ---------------------------
@router.get("/hello", summary="Introduce yourself")
def hello(
    name: str = Query(..., description="Your identifier for this tier.")
):
    if not re.fullmatch(r"[A-Za-z0-9_]{2,24}", name.strip()):
        raise HTTPException(status_code=400, detail="Identifier format invalid.")
    return {"message": "Welcome!", "flag": FLAG_HELLO}

# ---------------------------
# 2) REST discovery (clue + hidden resource)
# ---------------------------
@router.get("/discover", summary="Get a clue for a REST-style path")
def discover():
    """
    Non-spoiler clue:
    - Many APIs expose resources as plural nouns (e.g., /users, /posts).
    - The resource you need to find is a 'document'.
    - The document also needs an ID - the answer to life the universe and everything.
    """
    return {
        "message": "Find the resource and id. When ready, request it.",
        "example_style": "/bronze/<resource-name>/<id>"
    }

# Hidden endpoint: students must infer /bronze/documents/42
@router.get(
    "/documents/{doc_id}",
    include_in_schema=False,  # keep it out of Swagger to make them infer it
)
def documents(doc_id: int = Path(..., description="Document id")):
    if doc_id == 42:
        return {"title": "The Answer", "flag": FLAG_REST}
    raise HTTPException(status_code=404, detail="Document not found")

# ---------------------------
# 3) Echo (JSON body)
# ---------------------------
class EchoIn(BaseModel):
    phrase: str = Field(..., description="Short text to process.")

@router.post("/echo", summary="Send a short phrase (between 10 and 60 characters)")
def echo(body: EchoIn):
    """
    Non-spoiler clue:
    - This route expects a JSON formatted body.
    - The JSON has to be in the EchoIn-Schema format (also documented below).
    """
    p = body.phrase.strip()
    if len(p) < 10 or len(p) > 60:
        raise HTTPException(status_code=400, detail="Phrase length out of range.")
    return {"echo": p, "flag": FLAG_ECHO}

# ---------------------------
# 4) Client (User-Agent header)
# ---------------------------
@router.get("/client", summary="Identify your client")
def client(
    user_agent: str = Header(..., alias="User-Agent", description="Identify the requesting software.")
):
    """
    Non-spoiler clue:
    - It's good manners to always specify your client name (and email) in an User-Agent header, when you send an API request.
    - No need for an email here.
    - But - your client ID should be in the following format: LinguAPI-Client/{name}
    """
    # Expect a simple client signature
    if not user_agent.startswith("LinguAPI-Client/"):
        raise HTTPException(status_code=400, detail="Client signature not accepted.")
    name = user_agent.split("/", 1)[-1].strip()
    if not name:
        raise HTTPException(status_code=400, detail="Missing client identifier.")
    return {"message": f"Client accepted: {name}", "flag": FLAG_UA}

# ---------------------------
# 5) Final (verify static flags)
# ---------------------------
class FinalIn(BaseModel):
    flags: list[str] = Field(..., description="Four Bronze flags in order, separated with commas.")

@router.post("/final", summary="Submit flags to receive the Bronze trophy")
def final(body: FinalIn):
    expected = [FLAG_HELLO, FLAG_REST, FLAG_ECHO, FLAG_UA]
    if body.flags == expected:
        return {"trophy": "🥉", "flag": FLAG_FINAL}
    raise HTTPException(status_code=400, detail="Flags invalid or out of order.")
