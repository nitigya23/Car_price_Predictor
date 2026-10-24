import os
import json
import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Literal

# Load trained models and metadata
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "ford_model.joblib")
LR_MODEL_PATH = os.path.join(BASE_DIR, "ford_linear_model.joblib")
META_PATH = os.path.join(BASE_DIR, "model_metadata.json")

if not os.path.exists(MODEL_PATH) or not os.path.exists(META_PATH):
    raise RuntimeError("Model files not found! Please run train_model.py first.")

rf_model = joblib.load(MODEL_PATH)
lr_model = joblib.load(LR_MODEL_PATH)

with open(META_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

app = FastAPI(
    title="Ford Car Valuation AI",
    description="Minimal and sleek Machine Learning frontend for Ford car price prediction",
    version="1.0.0"
)

# Mount static and templates
static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "templates")

os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

class PredictionRequest(BaseModel):
    model: str = Field(..., example="Fiesta")
    year: int = Field(..., ge=1990, le=2025, example=2018)
    transmission: str = Field(..., example="Manual")
    fuelType: str = Field(..., example="Petrol")
    mileage: int = Field(..., ge=0, le=300000, example=24000)
    tax: int = Field(default=145, ge=0, le=600, example=145)
    mpg: float = Field(default=55.0, ge=10.0, le=250.0, example=58.9)
    engineSize: float = Field(default=1.0, ge=0.0, le=6.0, example=1.0)
    algorithm: Literal["random_forest", "linear_regression"] = "random_forest"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, model: Optional[str] = None):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "metadata": metadata,
            "selected_model": model or "Fiesta",
            "active_page": "valuation"
        }
    )

@app.get("/catalog", response_class=HTMLResponse)
async def catalog_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="catalog.html",
        context={
            "metadata": metadata,
            "active_page": "catalog"
        }
    )

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="analytics.html",
        context={
            "metadata": metadata,
            "active_page": "analytics"
        }
    )

@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={
            "metadata": metadata,
            "active_page": "about"
        }
    )

@app.get("/api/analytics-data")
async def get_analytics_data():
    return JSONResponse({
        "yearlyDepreciation": {
            "labels": ["2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"],
            "prices": [6704, 7542, 8778, 10666, 11966, 13158, 17176, 20820]
        },
        "transmissionPremiums": {
            "labels": ["Manual", "Semi-Auto", "Automatic"],
            "prices": [12024, 14932, 16118]
        },
        "fuelTypeAverages": {
            "labels": ["Petrol", "Diesel", "Hybrid", "Electric"],
            "prices": [11829, 13918, 22149, 15738]
        },
        "topModels": {
            "labels": ["Fiesta", "Focus", "Kuga", "EcoSport", "Mondeo", "Puma", "Mustang"],
            "prices": [10346, 13492, 15879, 12499, 13066, 19850, 34500]
        }
    })

@app.get("/api/metadata")
async def get_metadata():
    return JSONResponse(metadata)

@app.get("/api/defaults/{model_name}")
async def get_model_defaults(model_name: str, year: Optional[int] = None):
    model_data = metadata.get("model_defaults", {}).get(model_name)
    if not model_data:
        raise HTTPException(status_code=404, detail="Model not found in dataset")
    
    if year and str(year) in model_data.get("by_year", {}):
        return JSONResponse(model_data["by_year"][str(year)])
    elif year and year in model_data.get("by_year", {}):
        return JSONResponse(model_data["by_year"][year])
    
    return JSONResponse(model_data["overall"])

@app.post("/api/predict")
async def predict_price(payload: PredictionRequest):
    try:
        # Prepare single row dataframe matching training features
        input_dict = {
            'model': [payload.model.strip()],
            'transmission': [payload.transmission.strip()],
            'fuelType': [payload.fuelType.strip()],
            'year': [int(payload.year)],
            'mileage': [int(payload.mileage)],
            'tax': [int(payload.tax)],
            'mpg': [float(payload.mpg)],
            'engineSize': [float(payload.engineSize)]
        }
        df_input = pd.DataFrame(input_dict)

        # Select model
        selected_model = lr_model if payload.algorithm == "linear_regression" else rf_model
        predicted_val = float(selected_model.predict(df_input)[0])

        # Clamp prediction to logical minimum
        predicted_val = max(350.0, predicted_val)

        # Confidence bounds (standard error estimate from MAE)
        mae = metadata["metrics"][payload.algorithm]["mae"]
        low_bound = max(300.0, predicted_val - (mae * 0.85))
        high_bound = predicted_val + (mae * 0.85)

        # Benchmark comparison against average price for this model
        model_info = metadata["model_defaults"].get(payload.model.strip(), {}).get("overall", {})
        avg_model_price = model_info.get("avgPrice", metadata["dataset_summary"]["avg_price"])
        diff_pct = round(((predicted_val - avg_model_price) / avg_model_price) * 100, 1)

        # Market valuation rating
        if diff_pct < -15:
            valuation_tag = "Exceptional Value"
            badge_color = "emerald"
        elif diff_pct < 0:
            valuation_tag = "Competitive Deal"
            badge_color = "sky"
        elif diff_pct < 20:
            valuation_tag = "Fair Market Price"
            badge_color = "amber"
        else:
            valuation_tag = "Premium Spec / Low Mileage"
            badge_color = "purple"

        inr_val = round(predicted_val * 108.5)
        low_inr = round(low_bound * 108.5)
        high_inr = round(high_bound * 108.5)
        avg_inr = round(avg_model_price * 108.5)

        return JSONResponse({
            "success": True,
            "predictedPrice": round(predicted_val),
            "predictedPriceINR": inr_val,
            "predictedPriceFormatted": f"₹ {inr_val:,}",
            "predictedPriceGBP": f"£ {round(predicted_val):,}",
            "range": {
                "low": round(low_bound),
                "high": round(high_bound),
                "lowINR": low_inr,
                "highINR": high_inr,
                "formatted": f"₹ {low_inr:,} - ₹ {high_inr:,}",
                "formattedGBP": f"£ {round(low_bound):,} - £ {round(high_bound):,}"
            },
            "comparison": {
                "avgModelPrice": avg_model_price,
                "avgModelPriceINR": avg_inr,
                "diffPercentage": diff_pct,
                "tag": valuation_tag,
                "badgeColor": badge_color
            },
            "modelUsed": "Random Forest (R² 94%)" if payload.algorithm == "random_forest" else "Linear Regression (R² 86%)",
            "carSummary": f"{payload.year} Ford {payload.model} ({payload.engineSize}L {payload.fuelType})"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    port = 8000
    print(f"Starting sleek Ford Prediction App on http://localhost:{port}")
    webbrowser.open(f"http://localhost:{port}")
    uvicorn.run("app:app", host="127.0.0.1", port=port, reload=False)

