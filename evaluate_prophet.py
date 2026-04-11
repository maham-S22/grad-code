import pandas as pd
import numpy as np
import logging
from prophet import Prophet
from utils.data_loader import load_specific_sheet, save_sheet_to_excel

logging.getLogger('cmdstanpy').setLevel(logging.WARNING)

print("🔍 Extracting Clean Data for Dynamic Evaluation...")
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
print(f"🎯 Testing on Months {test_cols[0]} to {test_cols[-1]}...")

date_map = {str(m): pd.to_datetime('2023-01-01') + pd.DateOffset(months=m-1) for m in month_cols}
results = []

for index, row in df_clean.iterrows():
    product_name = row['MENU']
    
    history = row[train_cols].to_frame().reset_index()
    history.columns = ['Month', 'y']
    history['ds'] = history['Month'].map(date_map)
    df_train = history[['ds', 'y']].copy()
    
    use_yearly = True if len(train_cols) >= 24 else False
    
    m = Prophet(yearly_seasonality=use_yearly, weekly_seasonality=False, daily_seasonality=False)
    m.fit(df_train)
    
    future = m.make_future_dataframe(periods=12, freq='MS')
    forecast = m.predict(future)
    
    predictions = forecast['yhat'].iloc[-12:].values
    predictions = np.maximum(0, predictions)
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
        'Algorithm': 'Prophet',
        'MAD': round(mad, 2),
        'MSE': round(mse, 2),
        'WAPE': round(wape, 4), 
        'MAPE': round(mape, 4)  
    })

df_errors = pd.DataFrame(results)

print("💾 Writing Error Metrics to 'Prophet Errors' sheet...")
if save_sheet_to_excel(df_errors, "Prophet Errors"):
    print("✅ Dynamic Evaluation Complete!")
else:
    print("❌ Failed to write to database.")