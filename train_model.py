import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

def main():
    print("Loading dataset...")
    csv_paths = [
        r"c:\Users\DELL\Downloads\ford.csv",
        r".\ford.csv",
        r"..\ford.csv"
    ]
    df = None
    for p in csv_paths:
        if os.path.exists(p):
            df = pd.read_csv(p)
            print(f"Loaded dataset from {p}")
            break

    if df is None:
        raise FileNotFoundError("Could not find ford.csv in Downloads or local directory.")

    # Clean data
    # Strip whitespace from string columns
    for col in ['model', 'transmission', 'fuelType']:
        df[col] = df[col].astype(str).str.strip()

    # Filter out anomalous years (e.g. year 2060 in raw dataset) and positive prices
    df = df[(df['year'] >= 1990) & (df['year'] <= 2024)]
    df = df[df['price'] > 0]
    df = df.drop_duplicates()

    print(f"Cleaned dataset rows: {len(df)}")

    categorical_features = ['model', 'transmission', 'fuelType']
    numerical_features = ['year', 'mileage', 'tax', 'mpg', 'engineSize']
    target = 'price'

    X = df[categorical_features + numerical_features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features),
            ('num', StandardScaler(), numerical_features)
        ]
    )

    # Train high-performance model (Random Forest / HistGradientBoosting)
    print("Training Random Forest model...")
    rf_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=75, max_depth=16, random_state=42, n_jobs=1))
    ])
    rf_pipeline.fit(X_train, y_train)

    rf_preds = rf_pipeline.predict(X_test)
    rf_r2 = r2_score(y_test, rf_preds)
    rf_mae = mean_absolute_error(y_test, rf_preds)
    print(f"Random Forest - R2 Score: {rf_r2:.4f}, MAE: £{rf_mae:.2f}")

    # Also train Linear Regression (like in the user's notebook)
    print("Training Linear Regression model...")
    lr_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', LinearRegression())
    ])
    lr_pipeline.fit(X_train, y_train)
    lr_preds = lr_pipeline.predict(X_test)
    lr_r2 = r2_score(y_test, lr_preds)
    lr_mae = mean_absolute_error(y_test, lr_preds)
    print(f"Linear Regression - R2 Score: {lr_r2:.4f}, MAE: £{lr_mae:.2f}")

    # Compute model metadata & statistics per model and year
    models = sorted(df['model'].unique().tolist())
    years = sorted(df['year'].unique().tolist(), reverse=True)
    transmissions = sorted(df['transmission'].unique().tolist())
    fuel_types = sorted(df['fuelType'].unique().tolist())

    # Build smart lookup defaults for every model
    model_defaults = {}
    for m in models:
        m_df = df[df['model'] == m]
        # Most common transmission, fuelType, and median numerical values
        top_trans = m_df['transmission'].mode()[0] if not m_df['transmission'].empty else 'Manual'
        top_fuel = m_df['fuelType'].mode()[0] if not m_df['fuelType'].empty else 'Petrol'
        
        # Per-year defaults if available, else overall model defaults
        year_stats = {}
        for yr in sorted(m_df['year'].unique().tolist(), reverse=True):
            my_df = m_df[m_df['year'] == yr]
            year_stats[int(yr)] = {
                'mileage': int(round(my_df['mileage'].median())),
                'tax': int(round(my_df['tax'].median())),
                'mpg': round(float(my_df['mpg'].median()), 1),
                'engineSize': round(float(my_df['engineSize'].median()), 1),
                'transmission': my_df['transmission'].mode()[0],
                'fuelType': my_df['fuelType'].mode()[0],
                'avgPrice': int(round(my_df['price'].mean())),
                'minPrice': int(my_df['price'].min()),
                'maxPrice': int(my_df['price'].max())
            }

        model_defaults[m] = {
            'overall': {
                'mileage': int(round(m_df['mileage'].median())),
                'tax': int(round(m_df['tax'].median())),
                'mpg': round(float(m_df['mpg'].median()), 1),
                'engineSize': round(float(m_df['engineSize'].median()), 1),
                'transmission': top_trans,
                'fuelType': top_fuel,
                'avgPrice': int(round(m_df['price'].mean())),
                'count': len(m_df)
            },
            'by_year': year_stats,
            'available_years': sorted(list(year_stats.keys()), reverse=True)
        }

    # Save trained model & metadata
    out_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(out_dir, "ford_model.joblib")
    lr_model_path = os.path.join(out_dir, "ford_linear_model.joblib")
    meta_path = os.path.join(out_dir, "model_metadata.json")

    joblib.dump(rf_pipeline, model_path)
    joblib.dump(lr_pipeline, lr_model_path)

    metadata = {
        'models': models,
        'years': [int(y) for y in years],
        'transmissions': transmissions,
        'fuelTypes': fuel_types,
        'metrics': {
            'random_forest': {'r2': round(rf_r2, 4), 'mae': round(rf_mae, 2)},
            'linear_regression': {'r2': round(lr_r2, 4), 'mae': round(lr_mae, 2)}
        },
        'model_defaults': model_defaults,
        'dataset_summary': {
            'total_records': len(df),
            'min_price': int(df['price'].min()),
            'max_price': int(df['price'].max()),
            'avg_price': int(round(df['price'].mean()))
        }
    }

    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"Model saved successfully to: {model_path}")
    print(f"Metadata saved successfully to: {meta_path}")

if __name__ == "__main__":
    main()

