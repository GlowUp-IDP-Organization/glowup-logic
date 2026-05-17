import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="GlowUp Logic Service - Production")

# Primim ID-uri de produse, nu direct ingrediente
class RoutineRequest(BaseModel):
    product_ids: list[int]

@app.post("/analyze-routine")
def analyze_routine(request: RoutineRequest):
    try:
        # 1. Extragem toate produsele din baza de date
        response = requests.get("http://glowup_io:3000/products")
        response.raise_for_status()
        all_products = response.json().get("data", [])
        
        # 2. Filtram doar produsele bifate de utilizator
        selected_products = [p for p in all_products if p["id"] in request.product_ids]
        
        if len(selected_products) != len(request.product_ids):
            raise HTTPException(status_code=404, detail="Unul sau mai multe produse nu au fost gasite in baza de date.")

        # 3. Extragem si combinam ingredientele active
        ingredients = []
        for p in selected_products:
            # Impartim "Vitamina C, Niacinamide" in lista
            ing_list = [i.strip().lower() for i in p["active_ingredients"].split(",")]
            ingredients.extend(ing_list)

        # 4. Aplicam algoritmul
        has_retinol = any("retinol" in i for i in ingredients)
        has_acids = any(acid in i for i in ingredients for acid in ["aha", "bha", "acid glicolic", "acid salicilic"])
        
        product_names = [p["name"] for p in selected_products]
        
        if has_retinol and has_acids:
            return {
                "safe": False,
                "warning": "ALERTA: Combinarea Retinolului cu acizi AHA/BHA provoaca iritatii severe!",
                "routine_products": product_names
            }
            
        return {
            "safe": True,
            "message": "Rutina este sigura pentru tenul tau!",
            "routine_products": product_names
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Eroare severa la baza de date (IO MS): {str(e)}")