from django.db import models


# Create your models here.
class Consumer(models.Model):
    first_name = models.CharField(max_length=64)
    second_name = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=64, null=True)

class TelegramProfile(models.Model):
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE)
    chat_id = models.IntegerField(max_length=16)

class CreditRequest(models.Model):
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    status_ml = models.IntegerField(max_length=64, default=0)
    status_ma = models.IntegerField(max_length=64, default=0)
    seniority = models.IntegerField(max_length=16, default=0)
    home = models.IntegerField(max_length=8, default=0)
    time = models.IntegerField(max_length=64, default=0)
    age = models.IntegerField(max_length=64, default=0)
    marital = models.IntegerField(max_length=8, default=0)
    records = models.IntegerField(max_length=32, default=0)
    job = models.IntegerField(max_length=32, default=0)
    expenses = models.IntegerField(max_length=64, default=0)
    income = models.IntegerField(max_length=64, default=0)
    assets = models.IntegerField(max_length=16, default=0)
    debt = models.IntegerField(max_length=64, default=0)
    amount = models.IntegerField(max_length=64, default=0)
    price = models.IntegerField(max_length=64, default=0)