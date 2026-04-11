import pandas as pd
import numpy as np
import xgboost as xgb
from utils.data_loader import load_specific_sheet, save_sheet_to_excel

print("🚀 Extracting Clean Data for Future XGBoost Pipeline...")
df_clean = load_specific_sheet("Clean Data")

if df_clean.empty:
    print("❌ Failed to load Clean Data.")
    exit()

all_cols = df_clean.columns.tolist()
month_cols = sorted([int(c) for c in all_cols if str(c).isdigit()])
total_months = len(month_cols)

# We are predicting the next 12 months (37-48)
future_month_indices = list(range(total_months + 1, total_months + 13))
future_dates = pd.date_range(start='2026-01-01', periods=12, freq='MS')
future_cols = [d.strftime('%b %Y') for d in future_dates]

def create_features(month_numbers):
    df = pd.DataFrame({'Time_Index': month_numbers})
    df['Month_of_Year'] = ((df['Time_Index'] - 1) % 12) + 1
    return df

results = []

for index, row in df_clean.iterrows():
    product_name = row['MENU']
    
    # Train on all 36 months
    X_train = create_features(month_cols)
    y_train = row[[str(m) for m in month_cols]].values.astype(float)
    
    # Optimized params for supply chain forecasting
    model = xgb.XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.1, objective='reg:squarederror')
    model.fit(X_train, y_train)
    
    # Predict the future
    X_future = create_features(future_month_indices)
    predictions = model.predict(X_future)
    predictions = [max(0, round(val, 2)) for val in predictions]
    
    result_row = {'MENU': product_name}
    for col, pred in zip(future_cols, predictions):
        result_row[col] = pred
        
    results.append(result_row)

df_future_xgb = pd.DataFrame(results)

print("\n--- SNEAK PEEK OF FUTURE XGBOOST PREDICTIONS ---")
print(df_future_xgb.head())

print("\n💾 Writing predictions to 'XGBoostForecast' sheet...")
if save_sheet_to_excel(df_future_xgb, "XGBoostForecast"):
    print("✅ Future XGBoost Pipeline Complete!")
else:
    print("❌ Failed to write to database.")