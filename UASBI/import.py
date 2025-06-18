import pandas as pd
from business_intelligence.models import (
    Gender, Income, Region, Employment,
    MaritalStatus, ShoppingFrequency,
    CustomerProfile, ShoppingBehavior, MarketingTarget
)
from django.db import transaction

# Baca file CSV
df = pd.read_csv('Customer_Data.csv')
df.dropna(inplace=True)  # Hindari null saat insert

# Optional: normalisasi 'Target'
df['Target'] = df['Target'].apply(lambda x: str(x).strip().lower() in ['1', 'true', 'yes'])

@transaction.atomic  # pastikan transaksi utuh
def import_data():
    for _, row in df.iterrows():
        # Cek atau buat data master (get_or_create)
        gender_obj, _ = Gender.objects.get_or_create(gender=row['Gender'])
        income_obj, _ = Income.objects.get_or_create(annual_income_range=row['Annual_Income'])
        region_obj, _ = Region.objects.get_or_create(region=row['Region'])
        employment_obj, _ = Employment.objects.get_or_create(employment_status=row['Employment_Status'])
        marital_status_obj, _ = MaritalStatus.objects.get_or_create(marital_status=row['Marital_Status'])
        shopping_freq_obj, _ = ShoppingFrequency.objects.get_or_create(frequency_level=row['Online_Shopping_Frequency'])

        # Buat customer profile
        customer = CustomerProfile.objects.create(
            gender=gender_obj,
            income=income_obj,
            region=region_obj,
            num_of_children=int(row['Num_of_Children']),
            age=int(row['Age']),
        )

        # Buat shopping behavior
        ShoppingBehavior.objects.create(
            customer=customer,
            spending_score=int(row['Spending_Score']),
            credit_score=int(row['Credit_Score']),
            shopping_frequency=shopping_freq_obj,
            marital_status=marital_status_obj
        )

        # Buat marketing target
        MarketingTarget.objects.create(
            customer=customer,
            target_flag=row['Target'],
            employment=employment_obj,
            income=income_obj,     # income relasi duplikat
            region=region_obj      # region relasi duplikat
        )

    print(f"✅ Berhasil mengimpor {len(df)} data pelanggan.")

# Jalankan
import_data()
