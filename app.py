# backend/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend.routers import patient_routes, prediction_routes, recommendation_routes

app = FastAPI(title="Intelligent Health Platform")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Initialize DB (tables)
init_db()

# include routers
app.include_router(patient_routes.router)
app.include_router(prediction_routes.router)
app.include_router(recommendation_routes.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Intelligent Health Platform backend working."}

# Run with: uvicorn backend.app:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
