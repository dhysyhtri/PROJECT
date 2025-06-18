from django.shortcuts import render
from django.http import JsonResponse
import json
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAREHOUSE_PATH = '/root/airflow/dags/data_warehouse'

def dashboard_view(request):
    try:
        customer_df = pd.read_csv(os.path.join(WAREHOUSE_PATH, 'fact_customer_profile.csv'))
        marketing_df = pd.read_csv(os.path.join(WAREHOUSE_PATH, 'fact_marketing_target.csv'))
        behavior_df = pd.read_csv(os.path.join(WAREHOUSE_PATH, 'fact_shopping_behavior.csv'))
        dim_region = pd.read_csv(os.path.join(WAREHOUSE_PATH, 'dim_region.csv'))
    except Exception as e:
        return JsonResponse({'error': f'Failed to load ETL data: {str(e)}'})

    # Gabungkan dim_region ke customer_df agar Region tersedia
    if 'region_id' in customer_df.columns and 'region_id' in dim_region.columns:
        customer_df = customer_df.merge(dim_region[['region_id', 'Region']], on='region_id', how='left')

    # Gabungkan seluruh fact table SETELAH Region tersedia
    full_df = marketing_df.merge(behavior_df, on='customer_id', how='left') \
                          .merge(customer_df, on='customer_id', how='left')

    # 1. Distribusi pelanggan per Region dan Target Flag
    if 'Region' in full_df.columns and 'target_flag' in full_df.columns:
        dist_region_target = (
            full_df.groupby(['Region', 'target_flag'])
            .size()
            .reset_index(name='count')
            .to_dict(orient='records')
        )
    else:
        print("Kolom tidak ditemukan:", full_df.columns)
        dist_region_target = []
    print("dist_region_target:", json.dumps(dist_region_target, indent=2))


    # 2. Distribusi jumlah target vs non-target
    target_dist = full_df['target_flag'].value_counts().to_dict()
    target_dist_data = {
        'labels': ['Non-Target', 'Target'],
        'counts': [
            target_dist.get(0, 0),
            target_dist.get(1, 0)
        ]
    }

    # 3. Rata-rata frekuensi belanja online per target
    if 'shopping_frequency_id' in full_df.columns and 'target_flag' in full_df.columns:
        avg_freq_by_target = (
            full_df.groupby('target_flag')['shopping_frequency_id']
            .mean()
            .round(2)
            .to_dict()
        )
    else:
        avg_freq_by_target = {}

    # 4. Sebaran Spending Score per Target
    spending_distribution = {0: [], 1: []}
    for _, row in full_df.iterrows():
        flag = row['target_flag']
        score = row.get('spending_score', None)
        if pd.notnull(score):
            spending_distribution[int(flag)].append(score)

    # 5. Prediksi tren belanja online
    freq_counts = full_df['shopping_frequency_id'].value_counts().sort_index()
    freq_numeric = freq_counts.values
    labels = freq_counts.index.tolist()

    X = np.arange(len(freq_numeric)).reshape(-1, 1)
    y = freq_numeric
    model = LinearRegression().fit(X, y)

    future_steps = 3
    X_future = np.arange(len(freq_numeric) + future_steps).reshape(-1, 1)
    y_pred = model.predict(X_future)

    trend_data = {
        'labels': labels + [f'Future-{i+1}' for i in range(future_steps)],
        'actual': y.tolist() + [None]*future_steps,
        'predicted': y_pred.tolist()
    }

    context = {
        'dist_region_target': json.dumps(dist_region_target),
        'trend_data': json.dumps(trend_data),
        'spending_distribution': json.dumps(spending_distribution),
        'avg_freq_by_target': json.dumps(avg_freq_by_target),
        'target_dist_data': json.dumps(target_dist_data),
    }

    return render(request, 'dashboard/dashboard.html', context)
