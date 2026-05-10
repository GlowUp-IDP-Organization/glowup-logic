from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="GlowUp Logic Service")

class RoutineRequest(BaseModel):
    ingredients: list[str]

@app.get("/health")
def health_check():
    return {"status": "Logic Service is ready!"}

@app.post("/check-routine")
def check_routine(request: RoutineRequest):
    ingredients = [i.lower() for i in request.ingredients]

    # Verificăm incompatibilitatea principală: Retinol + Acizi Exfolianți
    has_retinol = any("retinol" in i for i in ingredients)
    has_acids = any(acid in i for i in ingredients for acid in ["aha", "bha", "acid glicolic", "acid salicilic"])

    if has_retinol and has_acids:
        return {
            "safe": False,
            "warning": "ALERTA: Combinarea Retinolului cu acizi AHA/BHA in aceeasi sesiune poate provoca iritatii severe si compromiterea barierei cutanate!",
            "ingredients_analyzed": request.ingredients
        }

    return {
        "safe": True,
        "message": "Rutina este sigura. Ingredientele sunt compatibile.",
        "ingredients_analyzed": request.ingredients
    }