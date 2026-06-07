import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pickle
import os

DATASET_PATH = '../Mahakumbh_Complete_Dataset.csv'
MODEL_SAVE_PATH = '../backend/app/core/visitor_model.pkl'

def main():
    print("Loading dataset...")
    # Load dataset
    df = pd.read_excel(DATASET_PATH, engine='openpyxl')
    
    # Feature Engineering: We want to predict Total Visitors based on the Year
    df['Total_Visitors'] = df['Domestic_Visitors'] + df['International_Visitors']
    
    # We filter for Prayagraj if the dataset contains multiple locations, but usually Mahakumbh is Prayagraj/Haridwar/Ujjain/Nashik
    # We will use all data but encode location if needed. Let's simplify and just predict based on Year for Prayagraj.
    df_prayagraj = df[df['Location'].str.contains('Prayagraj', case=False, na=False)].copy()
    if df_prayagraj.empty:
        df_prayagraj = df # fallback
        
    X = df_prayagraj[['Year']]
    y = df_prayagraj['Total_Visitors']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("\n--- Benchmarking ML Models ---")
    
    # Model 1: Random Forest
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    rf_mae = mean_absolute_error(y_test, rf_preds)
    rf_rmse = np.sqrt(mean_squared_error(y_test, rf_preds))
    print(f"Random Forest -> MAE: {rf_mae:,.2f} | RMSE: {rf_rmse:,.2f}")
    
    # Model 2: Gradient Boosting
    gb = GradientBoostingRegressor(n_estimators=100, random_state=42)
    gb.fit(X_train, y_train)
    gb_preds = gb.predict(X_test)
    gb_mae = mean_absolute_error(y_test, gb_preds)
    gb_rmse = np.sqrt(mean_squared_error(y_test, gb_preds))
    print(f"Gradient Boosting -> MAE: {gb_mae:,.2f} | RMSE: {gb_rmse:,.2f}")
    
    # Choose Best Model
    best_model = rf if rf_rmse < gb_rmse else gb
    best_name = "Random Forest" if rf_rmse < gb_rmse else "Gradient Boosting"
    
    print(f"\nWinning Model: {best_name}")
    
    # Predict for 2028 (The upcoming Mahakumbh)
    pred_2028 = best_model.predict([[2028]])[0]
    print(f"Predicted Total Visitors for 2028: {pred_2028:,.0f}")
    
    # Calculate a Global Congestion Multiplier (Baseline: 50 million visitors = 1.0 multiplier)
    base_visitors = 50_000_000
    multiplier = max(1.0, pred_2028 / base_visitors)
    print(f"Calculated Global Congestion Multiplier: {multiplier:.2f}x")
    
    # Save the model and the multiplier
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    with open(MODEL_SAVE_PATH, 'wb') as f:
        pickle.dump({
            "model": best_model,
            "multiplier": multiplier,
            "predicted_visitors": pred_2028
        }, f)
    print(f"Model saved to {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    main()
