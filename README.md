# Ford Car Valuation AI - Prestige Modern Edition 

An ultra-chic, high-fashion modern automotive intelligence platform built for Ford car price prediction. Powered by an ensemble Random Forest regressor with **94.01% $R^2$ accuracy** trained on 17,800+ real UK listings.

---

## 🌐 Modern Multi-Page Architecture & Hyperlinks

The platform features full inter-page navigation connecting dedicated experiences:

1. **[Valuation Studio (`/`)](file:///c:/Users/DELL/OneDrive/Desktop/DSA/ford_car_predictor/templates/index.html)**
   - Minimal & sleek prediction cockpit.
   - **Model Name & Year dropdowns** with dynamic smart auto-fill.
   - 1-click popular model preset pills (*Fiesta, Focus, Kuga, Mustang, Puma, Mondeo*).
   - High-end hero valuation card with animated price counters, multi-currency (£, $, ₹), confidence ranges, and deal badges.
   - Hyperlinks directly to Showroom, Analytics, and Architecture.

2. **[Model Showroom (`/catalog`)](file:///c:/Users/DELL/OneDrive/Desktop/DSA/ford_car_predictor/templates/catalog.html)**
   - Chic luxury catalog cards showcasing flagship vehicles (*Ford Mustang V8, Fiesta, Focus, Kuga SUV, Puma Hybrid, Mondeo Executive*).
   - Includes real dataset specs: typical engine displacement, MPG, and average resale price.
   - **"Value in Studio"** 1-click hyperlinks that pre-select that model inside the valuation calculator!

3. **[Market Analytics (`/analytics`)](file:///c:/Users/DELL/OneDrive/Desktop/DSA/ford_car_predictor/templates/analytics.html)**
   - Interactive Chart.js data visualizations:
     - **Depreciation Curve (2013 – 2020)** showing price erosion over time.
     - **Transmission Differential (+34% Automatic Premium)**.
     - **Model Resale Baseline Comparison**.
     - **Powertrain Fuel Economics (Hybrid £22.1k vs Petrol £11.8k)**.
   - Summary stat cards and deep market insights.

4. **[ML Architecture & Whitepaper (`/about`)](file:///c:/Users/DELL/OneDrive/Desktop/DSA/ford_car_predictor/templates/about.html)**
   - Comprehensive model architecture breakdown comparing **Random Forest (94.01% $R^2$, MAE £837)** vs **Linear Regression (85.77% $R^2$, MAE £1,351)**.
   - Feature importance rankings (Year 48%, Mileage 24%, Engine 14%).
   - Step-by-step pipeline documentation (`ColumnTransformer`, `OneHotEncoder`, `StandardScaler`).

5. **[Offline Standalone Preview (`standalone_preview.html`)](file:///c:/Users/DELL/OneDrive/Desktop/DSA/ford_car_predictor/standalone_preview.html)**
   - Zero-dependency client-side version that runs out of the box in Chrome/Edge with working tab links between all 4 views!

---

## 🚀 Quick Launch

### 1. Modern Web Application (Recommended)
Double-click `run_app.bat` or run:
```powershell
python app.py
```
> Automatically launches `http://localhost:8000` with the complete chic multi-page site.

### 2. Streamlit Dashboard
Double-click `run_streamlit.bat` or run:
```powershell
streamlit run streamlit_app.py
```
> Opens the 4-tab Streamlit edition on `http://localhost:8501`.

### 3. Instant Standalone Browser Preview
Simply double-click `standalone_preview.html` to explore the full interactive experience directly in your browser.
