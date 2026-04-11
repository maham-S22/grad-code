import pandas as pd
import logging
from prophet import Prophet
from utils.data_loader import load_specific_sheet, save_sheet_to_excel

logging.getLogger('cmdstanpy').setLevel(logging.WARNING)

print("Extracting Clean Data...")
df_clean = load_specific_sheet("Clean Data")

if df_clean.empty:
    print("Failed to load Clean Data.")
    exit()

train_cols = [str(i) for i in range(1, 25)] 
date_map = {str(1 + i): pd.to_datetime('2023-01-01') + pd.DateOffset(months=i) for i in range(24)}

results = []
print(f"Training Prophet models on 24 months of data for {len(df_clean)} products...")

for index, row in df_clean.iterrows():
    product_name = row['MENU']
    
    # 1. Melt historical data
    history = row[train_cols].to_frame().reset_index()
    history.columns = ['Month', 'y']
    history['ds'] = history['Month'].map(date_map)
    df_prophet = history[['ds', 'y']].copy()
    
    # 2. Train Prophet
    m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    m.fit(df_prophet)
    
    # 3. Generate future dataframe
    future = m.make_future_dataframe(periods=12, freq='MS')
    forecast = m.predict(future)
    
    # 4. Extract ONLY the future 12 months
    predictions = forecast.tail(12).copy()
    
    # 5. Pivot back to Wide Format with Date Headers (e.g., 'Jan 2025')
    row_result = {'MENU': product_name}
    for _, pred_row in predictions.iterrows():
        # Format the datestamp into a clean string for the column header
        col_name = pred_row['ds'].strftime('%b %Y')
        # The value under the column is the yhat
        row_result[col_name] = max(0, round(pred_row['yhat'], 2))
        
    results.append(row_result)

df_results = pd.DataFrame(results)

print("\n--- SNEAK PEEK OF WIDE DATE FORMAT ---")
print(df_results.head())
print("--------------------------------------\n")

print("Writing wide format predictions to 'PreviousProphet' sheet...")
if save_sheet_to_excel(df_results, "PreviousProphet"):
    print("Pipeline Complete! Check the PreviousProphet sheet.")
else:
    print("Failed to write to database.")