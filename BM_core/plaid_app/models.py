from django.db import models
from django.contrib.auth.models import User


class Item(models.Model):
    item_id = models.CharField(max_length=100, primary_key=True)
    access_token = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.item_id


class Account(models.Model):
    account_id = models.CharField(max_length=100, primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    balances = models.JSONField(null=True)
    mask = models.IntegerField(null=True)
    name = models.CharField(max_length=100, null=True)
    official_name = models.CharField(max_length=100, null=True)
    subtype = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.account_id


class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    account_owner = models.CharField(max_length=100, null=True)
    amount = models.FloatField()
    authorized_date = models.DateField(null=True)
    authorized_datetime = models.DateTimeField(null=True)
    category = models.JSONField(null=True)
    category_id = models.CharField(max_length=100, null=True)
    check_number = models.CharField(max_length=100, null=True)
    date = models.DateField(null=True)
    datetime = models.DateTimeField(null=True)
    iso_currency_code = models.CharField(max_length=10, null=True)
    location = models.JSONField(null=True)
    merchant_name = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=100, null=True)
    payment_channel = models.CharField(max_length=100, null=True)
    payment_meta = models.JSONField(null=True)
    pending = models.CharField(max_length=10, null=True)
    pending_transaction_id = models.CharField(max_length=100, null=True)
    personal_finance_category = models.CharField(max_length=100, null=True)
    transaction_code = models.CharField(max_length=100, null=True)
    transaction_id = models.CharField(max_length=100, primary_key=True)
    transaction_type = models.CharField(max_length=100, null=True)
    unofficial_currency_code = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.transaction_id
