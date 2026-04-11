import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import xgboost as xgb
from utils.data_loader import load_specific_sheet, save_sheet_to_excel

print("Extracting Clean Data for XGBoost Pipeline...")
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
print(f"Training XGBoost on Months {train_cols[0]} to {train_cols[-1]}...")

date_map = {str(m): pd.to_datetime('2023-01-01') + pd.DateOffset(months=m-1) for m in month_cols}
future_months = [total_months + i for i in range(1, 13)]
future_dates = [pd.to_datetime('2023-01-01') + pd.DateOffset(months=m-1) for m in future_months]

def create_features(month_numbers):
    df = pd.DataFrame({'Time_Index': month_numbers})
    df['Month_of_Year'] = ((df['Time_Index'] - 1) % 12) + 1
    return df

results = []
target_visual_items = ['A 004 02', 'A 111WK 28'] 

for index, row in df_clean.iterrows():
    product_name = row['MENU']
    
    X_train = create_features(month_cols)
    y_train = row[train_cols].values.astype(float)
    
    model = xgb.XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.1, objective='reg:squarederror')
    model.fit(X_train, y_train)
    
    if product_name in target_visual_items:
        os.makedirs("XGBoost_Visuals", exist_ok=True)
        safe_name = product_name.replace(" ", "_")
        
        plt.figure(figsize=(8, 5))
        xgb.plot_importance(model, importance_type='weight', title=f'XGBoost Feature Importance ({product_name})')
        plt.tight_layout()
        plt.savefig(f"XGBoost_Visuals/Feature_Importance_{safe_name}.png")
        plt.close()
        
        try:
            plt.figure(figsize=(20, 10))
            xgb.plot_tree(model, tree_idx=0)
            plt.savefig(f"XGBoost_Visuals/Decision_Tree_{safe_name}.png", dpi=300)
            plt.close()
        except Exception as e:
            print(f"\n[Note] Could not generate Tree Plot for {product_name}: You must install graphviz to plot tree")

    X_future = create_features(future_months)
    predictions = model.predict(X_future)
    predictions = np.maximum(0, predictions) 
    
    row_result = {'MENU': product_name}
    for i, pred_val in enumerate(predictions):
        col_name = future_dates[i].strftime('%b %Y')
        row_result[col_name] = max(0, round(pred_val, 2))
        
    results.append(row_result)

df_results = pd.DataFrame(results)

print("\n--- SNEAK PEEK OF XGBOOST PREDICTIONS ---")
print(df_results.head())
print("-----------------------------------------\n")

print("Writing predictions to 'PreviousXGBoost' sheet...")
if save_sheet_to_excel(df_results, "PreviousXGBoost"):
    print("XGBoost Pipeline Complete! Check your database and the XGBoost_Visuals folder.")
else:
    print("Failed to write to database.")