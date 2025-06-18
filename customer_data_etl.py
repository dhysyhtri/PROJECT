from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import os

dag_path = os.path.dirname(__file__)

def extract():
    df = pd.read_csv(os.path.join(dag_path, 'Customer_Data.csv'))
    df.to_csv('/tmp/extracted_data.csv', index=False)

def transform():
    df = pd.read_csv('/tmp/extracted_data.csv')

    # Buat dimensi unik
    dim_gender = df[['Gender']].drop_duplicates().reset_index(drop=True)
    dim_gender['gender_id'] = dim_gender.index + 1

    dim_income = df[['Annual_Income']].drop_duplicates().reset_index(drop=True)
    dim_income['income_id'] = dim_income.index + 1

    dim_region = df[['Region']].drop_duplicates().reset_index(drop=True)
    dim_region['region_id'] = dim_region.index + 1

    dim_employment = df[['Employment_Status']].drop_duplicates().reset_index(drop=True)
    dim_employment['employment_id'] = dim_employment.index + 1

    dim_marital = df[['Marital_Status']].drop_duplicates().reset_index(drop=True)
    dim_marital['marital_status_id'] = dim_marital.index + 1

    dim_freq = df[['Online_Shopping_Frequency']].drop_duplicates().reset_index(drop=True)
    dim_freq['shopping_frequency_id'] = dim_freq.index + 1

    # Gabung FK ke tabel fakta
    df = df.merge(dim_gender, on='Gender') \
           .merge(dim_income, on='Annual_Income') \
           .merge(dim_region, on='Region') \
           .merge(dim_employment, on='Employment_Status') \
           .merge(dim_marital, on='Marital_Status') \
           .merge(dim_freq, on='Online_Shopping_Frequency')

    # Buat tabel fakta
    fact_customer = df[['Customer_ID', 'gender_id', 'income_id', 'region_id', 'Num_of_Children', 'Age', 'Target']]
    fact_customer.columns = ['customer_id', 'gender_id', 'income_id', 'region_id', 'num_of_children', 'age', 'target_flag']

    fact_behavior = df[['Customer_ID', 'Spending_Score', 'Credit_Score', 'shopping_frequency_id', 'marital_status_id', 'Target']]
    fact_behavior.columns = ['customer_id', 'spending_score', 'credit_score', 'shopping_frequency_id', 'marital_status_id', 'target_flag']

    fact_marketing = df[['Customer_ID',  'employment_id', 'income_id', 'region_id', 'Target']]
    fact_marketing.columns = ['customer_id', 'employment_id', 'income_id', 'region_id', 'target_flag']

    # Simpan ke file (simulasi load ke data warehouse)
    dim_gender.to_csv('/tmp/dim_gender.csv', index=False)
    dim_income.to_csv('/tmp/dim_income.csv', index=False)
    dim_region.to_csv('/tmp/dim_region.csv', index=False)
    dim_employment.to_csv('/tmp/dim_employment.csv', index=False)
    dim_marital.to_csv('/tmp/dim_marital_status.csv', index=False)
    dim_freq.to_csv('/tmp/dim_shopping_frequency.csv', index=False)

    fact_customer.to_csv('/tmp/fact_customer_profile.csv', index=False)
    fact_behavior.to_csv('/tmp/fact_shopping_behavior.csv', index=False)
    fact_marketing.to_csv('/tmp/fact_marketing_target.csv', index=False)

def load():
    output_dir = os.path.join(dag_path, 'data_warehouse')
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir('/tmp'):
        if filename.startswith(('dim_', 'fact_')) and filename.endswith('.csv'):
            src = os.path.join('/tmp', filename)
            dst = os.path.join(output_dir, filename)
            pd.read_csv(src).to_csv(dst, index=False)

with DAG(
    dag_id='customer_data_etl',
    start_date=datetime(2023, 1, 1),
    schedule='@daily',
    catchup=False,
    tags=['etl', 'customer_data']
) as dag:

    t1 = PythonOperator(task_id='extract', python_callable=extract)
    t2 = PythonOperator(task_id='transform', python_callable=transform)
    t3 = PythonOperator(task_id='load', python_callable=load)

    t1 >> t2 >> t3
