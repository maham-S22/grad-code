import pandas as pd
from prophet import Prophet
from utils.data_loader import load_specific_sheet, save_sheet_to_excel

print("🔮 Extracting Clean Data for Future Prophet Pipeline...")
df_clean = load_specific_sheet("Clean Data")

if df_clean.empty:
    print("❌ Failed to load Clean Data.")
    exit()

all_cols = df_clean.columns.tolist()
month_cols = sorted([int(c) for c in all_cols if str(c).isdigit()])
total_months = len(month_cols)

print(f"📊 Detected {total_months} months of historical data.")
print("🚀 Training Prophet on all available history to predict the next 12 months...")

# Based on previous XGBoost logs, predictions start Jan 2026
train_dates = pd.date_range(end='2025-12-01', periods=total_months, freq='MS')
future_dates = pd.date_range(start='2026-01-01', periods=12, freq='MS')
future_cols = [d.strftime('%b %Y') for d in future_dates]

results = []

for index, row in df_clean.iterrows():
    product_name = row['MENU']
    
    # 1. Prep the full 36 months of data for this product
    df_train = pd.DataFrame({
        'ds': train_dates,
        'y': row[[str(m) for m in month_cols]].values.astype(float)
    })
    
    # 2. Train Prophet on ALL history (Logs will print normally)
    model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    model.fit(df_train)
    
    # 3. Predict Months 37-48
    df_future = pd.DataFrame({'ds': future_dates})
    forecast = model.predict(df_future)
    
    # Floor predictions at 0
    predictions = [max(0, round(val, 2)) for val in forecast['yhat'].values]
    
    # Map predictions to formatted month columns
    result_row = {'MENU': product_name}
    for col, pred in zip(future_cols, predictions):
        result_row[col] = pred
        
    results.append(result_row)

df_forecast = pd.DataFrame(results)

print("\n--- SNEAK PEEK OF FUTURE PROPHET PREDICTIONS ---")
print(df_forecast.head())
print("------------------------------------------------\n")

print("💾 Writing predictions to 'ProphetForecast' sheet...")
if save_sheet_to_excel(df_forecast, "ProphetForecast"):
    print("✅ Future Prophet Pipeline Complete!")
else:
    print("❌ Failed to write to database.")