from dotenv import load_dotenv
load_dotenv()  # loads .env file before anything else

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import youtube, pdf

app = FastAPI(title="Summarizer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(youtube.router, prefix="/api/youtube", tags=["YouTube"])
app.include_router(pdf.router,     prefix="/api/pdf",     tags=["PDF"])

@app.get("/")
def root():
    return {"message": "Summarizer API is running ✅"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
