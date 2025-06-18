from django.db import models

class Gender(models.Model):
    gender = models.CharField(max_length=10)

    def __str__(self):
        return self.gender

class Income(models.Model):
    annual_income_range = models.CharField(max_length=50)

    def __str__(self):
        return self.annual_income_range

class Region(models.Model):
    region = models.CharField(max_length=100)

    def __str__(self):
        return self.region

class Employment(models.Model):
    employment_status = models.CharField(max_length=30)

    def __str__(self):
        return self.employment_status

class MaritalStatus(models.Model):
    marital_status = models.CharField(max_length=20)

    def __str__(self):
        return self.marital_status

class ShoppingFrequency(models.Model):
    frequency_level = models.CharField(max_length=20)

    def __str__(self):
        return self.frequency_level

class CustomerProfile(models.Model):
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    income = models.ForeignKey(Income, on_delete=models.CASCADE)  # tetap ada
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    num_of_children = models.IntegerField()
    age = models.IntegerField()
    
    # Baru: data numerik aktual
    annual_income = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Customer {self.id} - Income: {self.annual_income}"

class ShoppingBehavior(models.Model):
    customer = models.OneToOneField(CustomerProfile, on_delete=models.CASCADE, primary_key=True)
    spending_score = models.IntegerField()
    credit_score = models.IntegerField()
    shopping_frequency = models.ForeignKey(ShoppingFrequency, on_delete=models.CASCADE)
    marital_status = models.ForeignKey(MaritalStatus, on_delete=models.CASCADE)

class MarketingTarget(models.Model):
    customer = models.OneToOneField(CustomerProfile, on_delete=models.CASCADE, primary_key=True)
    target_flag = models.BooleanField()
    employment = models.ForeignKey(Employment, on_delete=models.CASCADE)
    income = models.ForeignKey(Income, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
