# plaid-link-django-project

## Goal:

Plaid API integration with django using Plaid-Link. Link is a drop-in
module that handles credential validation, multi-factor authentication for
institution while keeping credentials from ever hitting theserver. 
Large asynchronous tasks are moved to celery. 

## Tech Stack:

Django, DRF, Celery, Redis, Nginx, Docker

## Steps to Setup:

- Clone the repository
- Run command: ```docker-compose up -d --build ```
- Access the backend django server at <a href="http://localhost:1337/">localhost:1337</a>
- Access the frontend nginx server at <a href="http://localhost:1338/">localhost:1338</a>
- Use the frontend to signup/login and access the plaid link to connect account.
- After successful link of the account, an asynchronous background task will start to fetch accounts and transactions for the linked account.
- Given API endpoints can be used to fetch transactions and accounts information.



## Postman

[![Run in Postman](https://run.pstmn.io/button.svg)](https://app.getpostman.com/run-collection/ce1f942959aabef195fa?action=collection%2Fimport)

- **Postman Collections:** [https://www.getpostman.com/collections/ce1f942959aabef195fa](https://www.getpostman.com/collections/ce1f942959aabef195fa)


## API Endpoints:

```http
POST /signup
```

| Parameter | Type      | Description                                                   |
| :-------- | :-------- | :------------------------------------------------------------ |
| `username`    | `string` | **Required**. username |
| `email`    | `string` | **Required**. email-id |
| `password`    | `string` | **Required**. password |

### Responses

```json
{
    "detail": "User created successfully",
    "token": "bf0914c6b55d9534d35d2c462e24bc569998cf9a"
}
```
```json
{
    "detail": "Username already exists.."
}
```
---

```http
POST /login
```

| Parameter | Type      | Description                                                   |
| :-------- | :-------- | :------------------------------------------------------------ |
| `username`    | `string` | **Required**. username |
| `password`    | `string` | **Required**. password |

### Responses

```json
{
    "token": "5511552527e95503e8cb11ed6e5187f4a4c43dc8",
    "user_id": 17
}
```
```json
{
    "detail": "Invalid username/password..."
}
```
---

```http
POST /logout
```

| Header     | Description                                                   |
| :------------ | :------------------------------------------------------------ |
| `Authorization`        | **Required**. Auth Token |

### Response

```json
{
    "detail": "Successfully logged out"
}
```
---

```http
POST /getlinktoken
```

| Header     | Description                                                   |
| :------------ | :------------------------------------------------------------ |
| `Authorization`        | **Required**. Auth Token |

### Responses

```json
{
    "expiration": "2022-06-30T14:27:26Z",
    "link_token": "link-sandbox-3c562718-ddfe-451f-9415-a9c58a1a2b0d",
    "request_id": "zrLhc5MZK9B2hEm"
}
```

---

```http
POST /getaccesstoken
```

| Header     | Description                                                   |
| :------------ | :------------------------------------------------------------ |
| `Authorization`        | **Required**. Auth Token |


| Parameter | Type      | Description                                                   |
| :-------- | :-------- | :------------------------------------------------------------ |
| `public_token`    | `string` | **Required**. Public-Toekn received after successfull link |

### Responses

```json
{
    "access_token": "access-sandbox-8ff3db16-03c2-48f0-a39e-b6a4a5628231",
    "item_id": "1Q3BEqgM7jHr1LEP9avAHdBKEpdbqau5Ned6p",
    "request_id": "JAmUiv96ofCwhMn"
}
```
---

```http
POST /getaccountdata
```
| Header     | Description                                                   |
| :------------ | :------------------------------------------------------------ |
| `Authorization`        | **Required**. Auth Token |

### Response

```json
{
    "error": null,
    "transactions": {
        "accounts": [
            {
                "account_id": "ZXrLPremDycvRVojB6l7fZlXmXAXgWtrMXoZr",
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
                "account_id": "MvbxyboKGNf3bwae8QVlIEbDMDRDamCe3Pja7",
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
            "item_id": "34za3zd9wXFX73ovVA5MSaGDag6XRohqXdb6g",
            "optional_products": null,
            "products": [
                "auth",
                "transactions"
            ],
            "update_type": "background",
            "webhook": ""
        },
        "request_id": "jLrgsgP0w1PZWWD"
    }
}
```

---

```http
POST /gettransactions
```
| Header     | Description                                                   |
| :------------ | :------------------------------------------------------------ |
| `Authorization`        | **Required**. Auth Token |

### Response

```json
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
```
## Screenshots

- **Server Log**

![Screenshot from 2022-06-30 23-45-48](https://user-images.githubusercontent.com/26035412/176759841-8cf49ed5-a8a9-4041-9805-c6ecd94119bb.png)

- **Frontend, Plaid-Link**

![Screenshot from 2022-06-30 23-29-12](https://user-images.githubusercontent.com/26035412/176759759-67f64368-f7ce-4aee-b975-f862c26200ff.png)
![Screenshot from 2022-06-30 23-29-48](https://user-images.githubusercontent.com/26035412/176759807-f07af98a-3bf3-453f-9083-86d9f3c0a6be.png)

- **In case if the requested resource is not ready on the plaid server, async fetch task will be retried after some delay**

![Screenshot from 2022-06-30 23-47-26](https://user-images.githubusercontent.com/26035412/176759913-d83adf52-c3a2-408b-b224-d75b77fdd441.png)





