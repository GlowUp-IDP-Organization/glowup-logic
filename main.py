import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="GlowUp Logic Service - Production")

class RoutineRequest(BaseModel):
    product_ids: list[int]

# --- 1. VERIFICATORUL DE INCOMPATIBILITĂȚI ---
@app.post("/analyze-routine")
def analyze_routine(request: RoutineRequest):
    try:
        response = requests.get("http://glowup_io:3000/products")
        response.raise_for_status()
        all_products = response.json().get("data", [])
        
        selected_products = [p for p in all_products if p["id"] in request.product_ids]
        
        if len(selected_products) != len(request.product_ids):
            raise HTTPException(status_code=404, detail="Unul sau mai multe produse nu au fost gasite.")

        ingredients = []
        for p in selected_products:
            ing_list = [i.strip().lower() for i in p["active_ingredients"].split(",")]
            ingredients.extend(ing_list)

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
        raise HTTPException(status_code=500, detail=f"Eroare la IO MS: {str(e)}")


# --- 2. GENERATORUL DE RUTINĂ INTELIGENT ---
@app.get("/generate-routine/{username}")
def generate_routine(username: str):
    try:
        # Preluăm produsele pe care utilizatorul le are efectiv pe raftul lui
        response = requests.get(f"http://glowup_io:3000/shelf/{username}")
        response.raise_for_status()
        shelf_items = response.json().get("shelf_items", [])

        if not shelf_items:
            return {"message": "Raftul tau este gol! Adauga produse mai intai.", "am_routine": [], "pm_routine": []}

        am_raw = []
        pm_raw = []

        # Împărțim produsele în funcție de momentul zilei permis (AM, PM sau BOTH)
        for item in shelf_items:
            # Obținem detaliile din catalog pentru acest produs
            # Deoarece ruta de shelf face JOIN, avem direct caracteristicile
            time_of_day = item.get("time_of_day", "BOTH")
            
            if time_of_day in ["AM", "BOTH"]:
                am_raw.append(item)
            if time_of_day in ["PM", "BOTH"]:
                pm_raw.append(item)

        # Sortăm listele în funcție de consistență (de la 1 la 5 - de la cel mai subțire la cel mai gros)
        am_sorted = sorted(am_raw, key=lambda x: x.get("consistency", 3))
        pm_sorted = sorted(pm_raw, key=lambda x: x.get("consistency", 3))

        # Extragem doar numele pentru un răspuns curat în interfață/terminal
        am_routine = [p["name"] for p in am_sorted]
        pm_routine = [p["name"] for p in pm_sorted]

        return {
            "username": username,
            "am_routine": am_routine,
            "pm_routine": pm_routine,
            "sorting_rule": "Produsele au fost ordonate corect din punct de vedere clinic: de la cea mai fluida consistenta la cea mai densa."
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Eroare la preluarea raftului din IO MS: {str(e)}")