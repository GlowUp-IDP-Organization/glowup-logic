import requests
from fastapi import FastAPI, HTTPException
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

@app.get("/analyze-all")
def analyze_all_products():
    try:
        # Python suna la adresa interna a containerului IO (pe portul 3000)
        response = requests.get("http://glowup_io:3000/products")
        response.raise_for_status() # Verifica daca a raspuns cu succes (200 OK)
        
        data = response.json()
        products = data.get("data", [])
        
        return {
            "message": f"Succes! Am preluat {len(products)} produse direct de la IO MS.",
            "database_items": products
        }
    except requests.exceptions.RequestException as e:
        # Aici facem Error Handling ca la carte
        raise HTTPException(status_code=500, detail=f"Eroare severa la comunicarea cu IO Service: {str(e)}")