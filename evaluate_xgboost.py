import pandas as pd
import numpy as np
import xgboost as xgb
from utils.data_loader import load_specific_sheet, save_sheet_to_excel

print("🔍 Extracting Clean Data for XGBoost Evaluation...")
df_clean = load_specific_sheet("Clean Data")

if df_clean.empty:
    print("❌ Failed to load Clean Data.")
    exit()

# DYNAMIC SPLIT LOGIC
all_cols = df_clean.columns.tolist()
month_cols = sorted([int(c) for c in all_cols if str(c).isdigit()])
total_months = len(month_cols)

if total_months <= 12:
    print(f"❌ Error: Only {total_months} months of data found. Need at least 13 months to test.")
    exit()

# Automatically reserve the last 12 months for testing
train_window = total_months - 12
train_cols = [str(m) for m in month_cols[:train_window]]
test_cols = [str(m) for m in month_cols[-12:]]

print(f"📊 Detected {total_months} total months.")
print(f"⚙️ Training on Months {train_cols[0]} to {train_cols[-1]}...")
print(f"🎯 Testing against Actuals in Months {test_cols[0]} to {test_cols[-1]}...")

def create_features(month_numbers):
    df = pd.DataFrame({'Time_Index': month_numbers})
    df['Month_of_Year'] = ((df['Time_Index'] - 1) % 12) + 1
    return df

results = []

for index, row in df_clean.iterrows():
    product_name = row['MENU']
    
    # Train on the first chunk
    X_train = create_features([int(m) for m in train_cols])
    y_train = row[train_cols].values.astype(float)
    
    model = xgb.XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.1, objective='reg:squarederror')
    model.fit(X_train, y_train)
    
    # Predict the test chunk
    X_test = create_features([int(m) for m in test_cols])
    predictions = model.predict(X_test)
    predictions = np.maximum(0, predictions)
    
    # Compare predictions to the TRUE ACTUALS
    actuals = row[test_cols].values.astype(float)
    
    errors = actuals - predictions
    abs_errors = np.abs(errors)
    
    mad = np.mean(abs_errors)
    mse = np.mean(errors ** 2)
    
    sum_actuals = np.sum(actuals)
    wape = np.sum(abs_errors) / sum_actuals if sum_actuals != 0 else 0
    
    non_zero_mask = actuals != 0
    if np.any(non_zero_mask):
        mape = np.mean(abs_errors[non_zero_mask] / actuals[non_zero_mask])
    else:
        mape = 0
        
    results.append({
        'MENU': product_name,
        'Algorithm': 'XGBoost',
        'MAD': round(mad, 2),
        'MSE': round(mse, 2),
        'WAPE': round(wape, 4), 
        'MAPE': round(mape, 4)  
    })

df_errors = pd.DataFrame(results)

print("💾 Writing Error Metrics to 'XGBoost Errors' sheet...")
if save_sheet_to_excel(df_errors, "XGBoost Errors"):
    print("✅ XGBoost Evaluation Complete! Your machine learning backend is finished.")
else:
    print("❌ Failed to write to database.")