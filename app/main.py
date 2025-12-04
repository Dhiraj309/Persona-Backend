from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException, Request

from .routers import auth, chat
from .config import FRONTEND_URL, INFERENCE_API_KEY

app = FastAPI(title = "YowAI")


app.add_middleware(
    CORSMiddleware,
    allow_origins = [FRONTEND_URL],
    allow_credentials = True,
    allow_headers = ["*"],
    allow_methods = ["*"]
)

app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return("Hello World!")

@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    protected_paths = [
        "/chat/",         # streaming chat endpoint
        "/chat"           # same
    ]

    # Only protect EXACT /chat/ (the inference endpoint)
    if request.url.path in protected_paths:
        auth = request.headers.get("Authorization")
        if not auth or auth != f"Bearer {INFERENCE_API_KEY}":
            raise HTTPException(status_code=401, detail="Unauthorized")

    return await call_next(request)