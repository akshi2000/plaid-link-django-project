from __future__ import absolute_import, unicode_literals
from BM_core.celery import app
from .models import Account, Item, Transaction
from .config import *
import datetime
import plaid

client = plaid.Client(
    PLAID_CLIENT_ID, PLAID_SECRET, environment=PLAID_ENV, api_version=PLAID_API_VERSION
)


@app.task(name="fetch_accounts_transactions", bind=True, max_retries=3)
def fetch_accounts_transactions(self, item_id):
    item = Item.objects.filter(item_id=item_id)[0]
    access_token = item.access_token

    try:
        # Fetching Accounts
        accounts_response = client.Accounts.get(access_token)
        accounts_data = accounts_response.get("accounts")
        """
        Sample Account Data from Plaid Server
        {
            "account_id": "kBBRxpQkbRu4Mnzz5zeKF3QAJDg8rEuJNralz",
            "balances": {
                "available": 200,
                "current": 210,
                "iso_currency_code": "USD",
                "limit": null,
                "unofficial_currency_code": null
            },
            "mask": "1111",
            "name": "Plaid Saving",
            "official_name": "Plaid Silver Standard 0.1% Interest Saving",
            "subtype": "savings",
            "type": "depository"
        }
        
        """
        # Saving Accounts data in database
        for account in accounts_data:
            # Check if this account has already been fetched
            if Account.objects.filter(account_id=account["account_id"]).count() > 0:
                continue
            new_account = Account.objects.create(
                account_id=account["account_id"],
                balances=account["balances"],
                item=item,
                mask=account["mask"],
                name=account["name"],
                official_name=account["official_name"],
                subtype=account["subtype"],
                type=account["type"],
            )

            new_account.save()

        """
        Sample transaction data from plaid server
        {
            "account_id": "kBBRxpQkbRu4Mnzz5zeKF3QAJDg8rEuJNralz",
            "account_owner": null,
            "amount": -4.22,
            "authorized_date": "2022-06-29",
            "authorized_datetime": null,
            "category": [
                "Transfer",
                "Credit"
            ],
            "category_id": "21005000",
            "check_number": null,
            "date": "2022-06-29",
            "datetime": null,
            "iso_currency_code": "USD",
            "location": {
                "address": null,
                "city": null,
                "country": null,
                "lat": null,
                "lon": null,
                "postal_code": null,
                "region": null,
                "store_number": null
            },
            "merchant_name": null,
            "name": "INTRST PYMNT",
            "payment_channel": "other",
            "payment_meta": {
                "by_order_of": null,
                "payee": null,
                "payer": null,
                "payment_method": null,
                "payment_processor": null,
                "ppd_id": null,
                "reason": null,
                "reference_number": null
            },
            "pending": false,
            "pending_transaction_id": null,
            "personal_finance_category": null,
            "transaction_code": null,
            "transaction_id": "kBBRxpQkbRu4Mnzz5ze9Uw1pQzVxjMHz5DLkR",
            "transaction_type": "special",
            "unofficial_currency_code": null
        },
        """

        start_date_time = datetime.datetime.today() - datetime.timedelta(days=2 * 365)
        start_date = str(start_date_time.date())
        end_date = str(datetime.date.today())

        # Fetching Transactions
        transactions_response = client.Transactions.get(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
        )
        transactions_data = transactions_response.get("transactions")

        # Saving Transactions
        for transaction in transactions_data:
            # Check if this transaction has already been fetched
            if (
                Transaction.objects.filter(
                    transaction_id=transaction["transaction_id"]
                ).count()
                > 0
            ):
                continue
            acc_id = transaction["account_id"]
            account = Account.objects.filter(account_id=acc_id)[0]
            new_transaction = Transaction.objects.create(
                account=account,
                account_owner=transaction["account_owner"],
                amount=transaction["amount"],
                authorized_date=transaction["authorized_date"],
                authorized_datetime=transaction["authorized_datetime"],
                category=transaction["category"],
                category_id=transaction["category_id"],
                check_number=transaction["check_number"],
                date=transaction["date"],
                datetime=transaction["datetime"],
                iso_currency_code=transaction["iso_currency_code"],
                location=transaction["location"],
                merchant_name=transaction["merchant_name"],
                name=transaction["name"],
                payment_channel=transaction["payment_channel"],
                payment_meta=transaction["payment_meta"],
                pending=transaction["pending"],
                pending_transaction_id=transaction["pending_transaction_id"],
                personal_finance_category=transaction["personal_finance_category"],
                transaction_code=transaction["transaction_code"],
                transaction_id=transaction["transaction_id"],
                transaction_type=transaction["transaction_type"],
                unofficial_currency_code=transaction["unofficial_currency_code"],
            )
            new_transaction.save()
        print("Successfully fetched accounts and transactions.")
    except Exception as e:
        print(e)
        print("Unable to fetch data from plaid server.")
        print("Retrying in " + str(3**self.request.retries) + " seconds")
        self.retry(countdown=3**self.request.retries)


@app.task(name="fetch_transactions", bind=True, max_retries=3)
def fetch_transactions(self, item_id, new_transactions):
    item = Item.objects.filter(item_id=item_id)[0]
    access_token = item.access_token
    try:
        start_date_time = datetime.datetime.today() - datetime.timedelta(days=2 * 365)
        start_date = str(start_date_time.date())
        end_date = str(datetime.date.today())

        # Fetching Updated Transactions
        transactions_response = client.Transactions.get(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            count=new_transactions,
        )
        transactions_data = transactions_response.get("transactions")

        # Saving Transactions
        for transaction in transactions_data:
            # Check if this transaction has already been fetched
            if (
                Transaction.objects.filter(
                    transaction_id=transaction["transaction_id"]
                ).count()
                > 0
            ):
                continue
            acc_id = transaction["account_id"]
            account = Account.objects.filter(account_id=acc_id)[0]
            new_transaction = Transaction.objects.create(
                account=account,
                account_owner=transaction["account_owner"],
                amount=transaction["amount"],
                authorized_date=transaction["authorized_date"],
                authorized_datetime=transaction["authorized_datetime"],
                category=transaction["category"],
                category_id=transaction["category_id"],
                check_number=transaction["check_number"],
                date=transaction["date"],
                datetime=transaction["datetime"],
                iso_currency_code=transaction["iso_currency_code"],
                location=transaction["location"],
                merchant_name=transaction["merchant_name"],
                name=transaction["name"],
                payment_channel=transaction["payment_channel"],
                payment_meta=transaction["payment_meta"],
                pending=transaction["pending"],
                pending_transaction_id=transaction["pending_transaction_id"],
                personal_finance_category=transaction["personal_finance_category"],
                transaction_code=transaction["transaction_code"],
                transaction_id=transaction["transaction_id"],
                transaction_type=transaction["transaction_type"],
                unofficial_currency_code=transaction["unofficial_currency_code"],
            )
            new_transaction.save()
        print("Successfully fetched new transactions.")
    except Exception as e:
        print(e)
        print("Unable to fetch data from plaid server.")
        print("Retrying in " + str(3**self.request.retries) + " seconds")
        self.retry(countdown=3**self.request.retries)


@app.task(name="delete_transactions", bind=True)
def delete_transactions(removed_transactions):
    for transaction in removed_transactions:
        Transaction.objects.filter(transaction_id=transaction).delete()


# Sample Response from plaid server
# Use it to save data accordingly
"""
{
    "error": null,
    "transactions": {
        "accounts": [
            {
                "account_id": "JXXy4QN9ayiwlbXXvXMZFQALVlzW7phQapxDQ",
                "balances": {
                    "available": 100,
                    "current": 110,
                    "iso_currency_code": "USD",
                    "limit": null,
                    "unofficial_currency_code": null
                },
                "mask": "0000",
                "name": "Plaid Checking",
                "official_name": "Plaid Gold Standard 0% Interest Checking",
                "subtype": "checking",
                "type": "depository"
            },
            {
                "account_id": "kBBRxpQkbRu4Mnzz5zeKF3QAJDg8rEuJNralz",
                "balances": {
                    "available": 200,
                    "current": 210,
                    "iso_currency_code": "USD",
                    "limit": null,
                    "unofficial_currency_code": null
                },
                "mask": "1111",
                "name": "Plaid Saving",
                "official_name": "Plaid Silver Standard 0.1% Interest Saving",
                "subtype": "savings",
                "type": "depository"
            }
        ],
        "item": {
            "available_products": [
                "assets",
                "balance",
                "credit_details",
                "identity",
                "income",
                "investments",
                "liabilities"
            ],
            "billed_products": [
                "auth",
                "transactions"
            ],
            "consent_expiration_time": null,
            "error": null,
            "institution_id": "ins_3",
            "item_id": "rPP6gKW9R6i5ZJvvpv7auXb3kZZAMmilpL5vn",
            "optional_products": null,
            "products": [
                "auth",
                "transactions"
            ],
            "update_type": "background",
            "webhook": ""
        },
        "request_id": "Ji7SWzwIiBRTkJY",
        "total_transactions": 98,
        "transactions": [
            {
                "account_id": "JXXy4QN9ayiwlbXXvXMZFQALVlzW7phQapxDQ",
                "account_owner": null,
                "amount": 4.33,
                "authorized_date": "2021-08-05",
                "authorized_datetime": null,
                "category": [
                    "Food and Drink",
                    "Restaurants",
                    "Coffee Shop"
                ],
                "category_id": "13005043",
                "check_number": null,
                "date": "2021-08-05",
                "datetime": null,
                "iso_currency_code": "USD",
                "location": {
                    "address": null,
                    "city": null,
                    "country": null,
                    "lat": null,
                    "lon": null,
                    "postal_code": null,
                    "region": null,
                    "store_number": null
                },
                "merchant_name": "Starbucks",
                "name": "Starbucks",
                "payment_channel": "in store",
                "payment_meta": {
                    "by_order_of": null,
                    "payee": null,
                    "payer": null,
                    "payment_method": null,
                    "payment_processor": null,
                    "ppd_id": null,
                    "reason": null,
                    "reference_number": null
                },
                "pending": false,
                "pending_transaction_id": null,
                "personal_finance_category": null,
                "transaction_code": null,
                "transaction_id": "EXXLwnBvNLivG4WWdWjbUmdw1wRPkjc9ne4Py",
                "transaction_type": "place",
                "unofficial_currency_code": null
            }
        ]
    }
}

"""
