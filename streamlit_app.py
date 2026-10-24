import os
import json
import joblib
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Ford AI | Prestige Car Valuation Studio",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Chic Luxury CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background-color: #060911;
        color: #f1f5f9;
    }

    /* Chic Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #0d1424;
        padding: 6px;
        border-radius: 9999px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        width: fit-content;
        margin-bottom: 24px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 38px;
        border-radius: 9999px;
        color: #94a3b8;
        font-size: 0.82rem;
        font-weight: 600;
        padding: 0 20px;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
    }

    .metric-card {
        background: linear-gradient(180deg, #141e3a 0%, #0c1426 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 24px;
        padding: 28px;
        box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.6);
        margin-bottom: 20px;
    }
    
    .price-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 3.4rem;
        font-weight: 800;
        color: #38bdf8;
        line-height: 1.1;
        letter-spacing: -1.5px;
    }
    
    .badge-deal {
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34d399;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 9999px;
    }

    .showroom-card {
        background: #0d1424;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Load Models & Metadata
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "ford_model.joblib")
LR_MODEL_PATH = os.path.join(BASE_DIR, "ford_linear_model.joblib")
META_PATH = os.path.join(BASE_DIR, "model_metadata.json")

@st.cache_resource
def load_resources():
    rf = joblib.load(MODEL_PATH)
    lr = joblib.load(LR_MODEL_PATH)
    with open(META_PATH, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    return rf, lr, meta

rf_model, lr_model, metadata = load_resources()

# Chic Top Banner
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0 20px 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 20px;">
    <div>
        <span style="font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 800; color: #ffffff;">
            FORD<span style="color: #38bdf8;">.AI</span> <span style="font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.3); color: #38bdf8; padding: 3px 8px; border-radius: 9999px; vertical-align: middle;">PRESTIGE</span>
        </span>
        <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 2px;">
            High-Performance Automotive Valuation & Analytics
        </div>
    </div>
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #34d399; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.25); padding: 5px 12px; border-radius: 9999px;">
        ● R² 94.01% Verified • 17,800+ Sales
    </div>
</div>
""", unsafe_allow_html=True)

# Chic Navigation Tabs
tab_val, tab_show, tab_ana, tab_doc = st.tabs([
    "⚡ Valuation Studio",
    "🏎️ Model Showroom",
    "📈 Market Analytics",
    "🧠 Architecture & Whitepaper"
])

# TAB 1: VALUATION STUDIO
with tab_val:
    col_form, col_pred = st.columns([7, 5], gap="large")

    with col_form:
        st.markdown("##### 1. Vehicle Identification")
        c1, c2 = st.columns(2)
        with c1:
            models = metadata["models"]
            selected_model = st.selectbox("Model Name", models, index=models.index("Fiesta") if "Fiesta" in models else 0)

        model_defaults = metadata["model_defaults"].get(selected_model, {})
        available_years = model_defaults.get("available_years", metadata["years"])
        with c2:
            default_year_idx = available_years.index(2018) if 2018 in available_years else 0
            selected_year = st.selectbox("Registration Year", available_years, index=default_year_idx)

        # Smart defaults
        year_stats = model_defaults.get("by_year", {}).get(str(selected_year)) or model_defaults.get("overall", {})
        def_trans = year_stats.get("transmission", "Manual")
        def_fuel = year_stats.get("fuelType", "Petrol")
        def_mileage = year_stats.get("mileage", 25000)
        def_engine = float(year_stats.get("engineSize", 1.0))
        def_mpg = float(year_stats.get("mpg", 58.0))
        def_tax = int(year_stats.get("tax", 145))

        st.markdown("##### 2. Technical Configuration")
        c3, c4 = st.columns(2)
        with c3:
            transmissions = metadata["transmissions"]
            selected_trans = st.selectbox("Transmission", transmissions, index=transmissions.index(def_trans) if def_trans in transmissions else 0)
        with c4:
            fuel_types = metadata["fuelTypes"]
            selected_fuel = st.selectbox("Fuel Type", fuel_types, index=fuel_types.index(def_fuel) if def_fuel in fuel_types else 0)

        selected_mileage = st.slider("Odometer Mileage (miles)", 500, 150000, def_mileage, 500)

        c5, c6, c7 = st.columns(3)
        with c5:
            selected_engine = st.number_input("Engine Size (L)", 0.5, 5.0, def_engine, 0.1)
        with c6:
            selected_mpg = st.number_input("Economy (MPG)", 15.0, 200.0, def_mpg, 0.5)
        with c7:
            selected_tax = st.number_input("Road Tax (£)", 0, 580, def_tax, 5)

        algo_choice = st.radio("Inference Engine", ["Random Forest (94% Accuracy)", "Linear Regression (Baseline)"], horizontal=True)

    # Prediction
    model_to_use = rf_model if "Random Forest" in algo_choice else lr_model
    input_df = pd.DataFrame([{
        'model': selected_model,
        'transmission': selected_trans,
        'fuelType': selected_fuel,
        'year': int(selected_year),
        'mileage': int(selected_mileage),
        'tax': int(selected_tax),
        'mpg': float(selected_mpg),
        'engineSize': float(selected_engine)
    }])

    predicted_price = float(model_to_use.predict(input_df)[0])
    predicted_price = max(350.0, predicted_price)
    rounded_price = round(predicted_price)
    mae = 837.0 if "Random Forest" in algo_choice else 1351.0
    low_range = max(300, round(predicted_price - mae * 0.85))
    high_range = round(predicted_price + mae * 0.85)
    avg_model_price = model_defaults.get("overall", {}).get("avgPrice", metadata["dataset_summary"]["avg_price"])
    diff_pct = round(((predicted_price - avg_model_price) / avg_model_price) * 100, 1)

    inr_price = round(predicted_price * 108.5)
    low_range_inr = round(low_range * 108.5)
    high_range_inr = round(high_range * 108.5)
    avg_model_price_inr = round(avg_model_price * 108.5)

    with col_pred:
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; font-weight: 600;">
                    Estimated Market Value (INR)
                </span>
                <span class="badge-deal">
                    {'Competitive Deal' if diff_pct <= 0 else 'Premium Spec'}
                </span>
            </div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #ffffff; margin-bottom: 4px;">
                {selected_year} Ford {selected_model}
            </div>
            <div style="font-size: 0.8rem; color: #64748b; font-family: 'JetBrains Mono', monospace; margin-bottom: 24px;">
                {selected_engine}L {selected_fuel} • {selected_trans} • {selected_mileage:,} miles
            </div>
            <div class="price-value">
                ₹ {inr_price:,}
            </div>
            <div style="font-size: 0.85rem; color: #38bdf8; font-family: 'JetBrains Mono', monospace; margin-top: 4px;">
                (≈ £{rounded_price:,} GBP)
            </div>
            <div style="margin-top: 20px; padding: 14px; background: rgba(8, 13, 26, 0.85); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #cbd5e1; display: flex; justify-content: space-between;">
                <span>Expected Range:</span>
                <span style="color: #ffffff; font-weight: 600;">₹ {low_range_inr:,} – ₹ {high_range_inr:,}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        m1, m2 = st.columns(2)
        with m1:
            st.metric("Model Baseline Average", f"₹ {avg_model_price_inr:,}")
        with m2:
            st.metric("Position vs Baseline", f"{'+' if diff_pct > 0 else ''}{diff_pct}%", delta=f"{-diff_pct}% relative value")

# TAB 2: SHOWROOM
with tab_show:
    st.markdown("### 🏎️ Ford Model Showroom")
    st.caption("Key models cataloged in the 17,800+ UK vehicle sales dataset.")
    
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        st.markdown("""
        <div class="showroom-card" style="border-color: rgba(245, 158, 11, 0.3);">
            <span style="font-size: 0.65rem; color: #f59e0b; background: rgba(245, 158, 11, 0.15); padding: 3px 8px; border-radius: 9999px; font-weight: 600;">PERFORMANCE FLAGSHIP</span>
            <h4 style="color: #ffffff; margin: 8px 0 4px 0;">Ford Mustang</h4>
            <p style="font-size: 0.8rem; color: #94a3b8;">5.0L V8 naturally aspirated pony car. Exceptional resale retention.</p>
            <div style="font-family: 'JetBrains Mono'; font-size: 0.85rem; color: #f59e0b; font-weight: 700; margin-top: 10px;">Avg: £34,500</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="showroom-card">
            <span style="font-size: 0.65rem; color: #38bdf8; background: rgba(56, 189, 248, 0.15); padding: 3px 8px; border-radius: 9999px; font-weight: 600;">FAMILY SUV</span>
            <h4 style="color: #ffffff; margin: 8px 0 4px 0;">Ford Kuga</h4>
            <p style="font-size: 0.8rem; color: #94a3b8;">Spacious midsize crossover with intelligent AWD. Over 2,200 dataset rows.</p>
            <div style="font-family: 'JetBrains Mono'; font-size: 0.85rem; color: #38bdf8; font-weight: 700; margin-top: 10px;">Avg: £15,879</div>
        </div>
        """, unsafe_allow_html=True)

    with s_col2:
        st.markdown("""
        <div class="showroom-card">
            <span style="font-size: 0.65rem; color: #34d399; background: rgba(16, 185, 129, 0.15); padding: 3px 8px; border-radius: 9999px; font-weight: 600;">UK BEST SELLER</span>
            <h4 style="color: #ffffff; margin: 8px 0 4px 0;">Ford Fiesta</h4>
            <p style="font-size: 0.8rem; color: #94a3b8;">Britain's top supermini. 6,400+ verified listings. 58.9 MPG economy.</p>
            <div style="font-family: 'JetBrains Mono'; font-size: 0.85rem; color: #34d399; font-weight: 700; margin-top: 10px;">Avg: £10,346</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="showroom-card">
            <span style="font-size: 0.65rem; color: #a855f7; background: rgba(168, 85, 247, 0.15); padding: 3px 8px; border-radius: 9999px; font-weight: 600;">ECOBOOST HYBRID</span>
            <h4 style="color: #ffffff; margin: 8px 0 4px 0;">Ford Puma</h4>
            <p style="font-size: 0.8rem; color: #94a3b8;">Mild-hybrid modern crossover with MegaBox underfloor luggage storage.</p>
            <div style="font-family: 'JetBrains Mono'; font-size: 0.85rem; color: #a855f7; font-weight: 700; margin-top: 10px;">Avg: £19,850</div>
        </div>
        """, unsafe_allow_html=True)

    with s_col3:
        st.markdown("""
        <div class="showroom-card">
            <span style="font-size: 0.65rem; color: #38bdf8; background: rgba(56, 189, 248, 0.15); padding: 3px 8px; border-radius: 9999px; font-weight: 600;">CLASS BENCHMARK</span>
            <h4 style="color: #ffffff; margin: 8px 0 4px 0;">Ford Focus</h4>
            <p style="font-size: 0.8rem; color: #94a3b8;">Dynamic family hatchback. 4,400+ listings with proven reliability.</p>
            <div style="font-family: 'JetBrains Mono'; font-size: 0.85rem; color: #38bdf8; font-weight: 700; margin-top: 10px;">Avg: £13,492</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="showroom-card">
            <span style="font-size: 0.65rem; color: #94a3b8; background: rgba(148, 163, 184, 0.15); padding: 3px 8px; border-radius: 9999px; font-weight: 600;">EXECUTIVE SALOON</span>
            <h4 style="color: #ffffff; margin: 8px 0 4px 0;">Ford Mondeo</h4>
            <p style="font-size: 0.8rem; color: #94a3b8;">Long-distance motorway touring comfort with acoustic glass cabin.</p>
            <div style="font-family: 'JetBrains Mono'; font-size: 0.85rem; color: #94a3b8; font-weight: 700; margin-top: 10px;">Avg: £13,066</div>
        </div>
        """, unsafe_allow_html=True)

# TAB 3: MARKET ANALYTICS
with tab_ana:
    st.markdown("### 📈 Market Resale Trends & Depreciation")
    st.caption("Visualizing pricing velocity across 17,800+ UK records.")

    deprec_df = pd.DataFrame({
        "Year": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020],
        "Average Price (£)": [6704, 7542, 8778, 10666, 11966, 13158, 17176, 20820]
    }).set_index("Year")
    
    st.line_chart(deprec_df)

    c_trans, c_fuel = st.columns(2)
    with c_trans:
        st.markdown("##### Transmission Premium")
        trans_df = pd.DataFrame({
            "Transmission": ["Manual", "Semi-Auto", "Automatic"],
            "Average Price (£)": [12024, 14932, 16118]
        }).set_index("Transmission")
        st.bar_chart(trans_df)

    with c_fuel:
        st.markdown("##### Powertrain Pricing")
        fuel_df = pd.DataFrame({
            "Powertrain": ["Petrol", "Diesel", "Electric", "Hybrid"],
            "Average Price (£)": [11829, 13918, 15738, 22149]
        }).set_index("Powertrain")
        st.bar_chart(fuel_df)

# TAB 4: ARCHITECTURE
with tab_doc:
    st.markdown("### 🧠 Machine Learning Architecture & Whitepaper")
    st.markdown("""
    - **Random Forest Regressor**: 75 estimator trees, max depth 16. Achieves **R² = 94.01%** and MAE = **£837.84**.
    - **Linear Regression**: Baseline ordinary least squares regressor with **R² = 85.77%** and MAE = **£1,351.27**.
    - **Preprocessing Pipeline**: Categorical columns (`model`, `transmission`, `fuelType`) one-hot encoded; continuous numericals standard-scaled.
    - **Key Valuation Weights**: Registration Year (~48%), Odometer Mileage (~24%), Engine Displacement (~14%).
    """)
