import pandas as pd
import logging
from prophet import Prophet
from utils.data_loader import load_specific_sheet, save_sheet_to_excel

logging.getLogger('cmdstanpy').setLevel(logging.WARNING)

print("Extracting Clean Data for Dynamic Production Pipeline...")
df_clean = load_specific_sheet("Clean Data")

if df_clean.empty:
    print("Failed to load Clean Data.")
    exit()

# DYNAMIC LOGIC
all_cols = df_clean.columns.tolist()
month_cols = sorted([int(c) for c in all_cols if str(c).isdigit()])
total_months = len(month_cols)

train_cols = [str(m) for m in month_cols] 

print(f"Detected {total_months} months of historical data.")
print(f"Training models on Months {train_cols[0]} to {train_cols[-1]}...")

# Automatically map whatever the final month is to the next 12 months
date_map = {str(m): pd.to_datetime('2023-01-01') + pd.DateOffset(months=m-1) for m in month_cols}
results = []

for index, row in df_clean.iterrows():
    product_name = row['MENU']
    
    history = row[train_cols].to_frame().reset_index()
    history.columns = ['Month', 'y']
    history['ds'] = history['Month'].map(date_map)
    df_prophet = history[['ds', 'y']].copy()
    
    use_yearly = True if total_months >= 24 else False
    m = Prophet(yearly_seasonality=use_yearly, weekly_seasonality=False, daily_seasonality=False)
    m.fit(df_prophet)
    
    # Predict the UNKNOWN future (Next 12 months)
    future = m.make_future_dataframe(periods=12, freq='MS')
    forecast = m.predict(future)
    predictions = forecast.tail(12).copy()
    
    # Pivot to Wide Format with Clean Date Headers
    row_result = {'MENU': product_name}
    for _, pred_row in predictions.iterrows():
        col_name = pred_row['ds'].strftime('%b %Y')
        row_result[col_name] = max(0, round(pred_row['yhat'], 2))
        
    results.append(row_result)

df_results = pd.DataFrame(results)

print("\n--- SNEAK PEEK OF DYNAMIC WIDE FORMAT ---")
print(df_results.head())
print("-----------------------------------------\n")

print("Writing predictions to 'PreviousProphet' sheet...")
if save_sheet_to_excel(df_results, "PreviousProphet"):
    print("Pipeline Complete! Check your database.")
else:
    print("Failed to write to database.")