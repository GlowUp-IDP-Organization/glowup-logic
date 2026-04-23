from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="GlowUp Logic Service")

# Definim cum arată datele pe care le așteptăm de la utilizator
class RoutineRequest(BaseModel):
    ingredients: list[str]

# Endpoint de test pentru starea serviciului
@app.get("/health")
def health_check():
    return {"status": "Logic Service is running and ready!"}

# Endpoint-ul principal 
@app.post("/check-routine")
def check_routine(request: RoutineRequest):
    # Deocamdată returnăm un răspuns de succes fals, logica o facem pentru Etapa 3
    return {
        "message": "Routine checked successfully",
        "safe": True,
        "ingredients_analyzed": request.ingredients
    }