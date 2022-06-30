from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .config import *
from .models import Item
from .tasks import fetch_accounts_transactions, delete_transactions, fetch_transactions
import datetime
import json
import plaid
import requests

client = plaid.Client(
    PLAID_CLIENT_ID, PLAID_SECRET, environment=PLAID_ENV, api_version=PLAID_API_VERSION
)


@api_view(["POST"])
def signupView(request):
    try:
        request_data = json.loads(request.body)
        username = request_data.get("username")
        email = request_data.get("email")
        password = request_data.get("password")
        if User.objects.filter(username=username).count() > 0:
            return Response(
                {"detail": "Username already exists.."},
                status=status.HTTP_409_CONFLICT,
            )
        user = User.objects.create_user(username, email, password)
        token = Token.objects.create(user=user)

        return Response(
            {"detail": "User created successfully", "token": token.key},
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        print(e)
        return Response(
            {"detail": "Bad email or weak password.."},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
def loginView(request):
    try:
        request_data = json.loads(request.body)
        username = request_data.get("username")
        password = request_data.get("password")
        user = authenticate(username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid username/password..."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            login(request, user)
            token = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token[0].key,
                "user_id": user.pk,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        print(e)
        return Response({}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def logoutView(request):
    request.user.auth_token.delete()
    return Response(
        data={"detail": "Successfully logged out"}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def getAccessToken(request):
    try:
        request_data = json.loads(request.body)
        public_token = request_data.get("public_token")
        exchange_response = client.Item.public_token.exchange(public_token)
        access_token = exchange_response["access_token"]
        item = Item.objects.create(
            access_token=access_token,
            item_id=exchange_response["item_id"],
            user=request.user,
        )
        item.save()
        print("starting fetch_accounts_transactions async task...")
        fetch_accounts_transactions.delay(item.item_id)
        return Response(exchange_response, status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def getTransaction(request):
    try:
        item = Item.objects.filter(user=request.user)
        if item.count() == 0:
            return Response(
                {
                    "detail": "No account is linked for the user. Please link account before fetching transactions"
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        access_token = item.values("access_token")[0]["access_token"]

        start_date_time = datetime.datetime.today() - datetime.timedelta(days=2 * 365)
        start_date = str(start_date_time.date())
        end_date = str(datetime.date.today())

        try:
            transactions_response = client.Transactions.get(
                access_token, start_date=start_date, end_date=end_date
            )
        except Exception as e:
            print(e)
            return Response(
                {"detail": "Unable to fetch transactions from Plaid server"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            data={"error": None, "transactions": transactions_response},
            status=status.HTTP_200_OK,
        )
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def getAccountData(request):
    try:
        item = Item.objects.filter(user=request.user)
        if item.count() == 0:
            return Response(
                {
                    "detail": "No account is linked for the user. Please link account before fetching transactions"
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        access_token = item.values("access_token")[0]["access_token"]
        try:
            accounts_response = client.Accounts.get(access_token)
        except Exception as e:
            print(e)
            return Response(
                {"detail": "Unable to fetch accounts from Plaid server"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            data={"error": None, "transactions": accounts_response},
            status=status.HTTP_200_OK,
        )
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def getLinkToken(request):
    url = "https://sandbox.plaid.com/link/token/create"
    headers = {"content-type": "application/json"}
    body = {
        "client_name": "Akshit's Plaid Django App",
        "client_id": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
        "country_codes": ["US"],
        "language": "en",
        "user": {"client_user_id": "1"},
        "products": ["auth"],
    }
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return Response(data=response.json(), status=status.HTTP_200_OK)


@api_view(["POST"])
def webhook(request):
    try:
        request_data = json.loads(request.body)
        webhook_type = request_data.get("webhook_type")
        webhook_code = request_data.get("webhook_code")

        if webhook_type == "TRANSACTIONS":
            item_id = request_data.get("item_id")
            if webhook_code == "TRANSACTIONS_REMOVED":
                removed_transactions = request_data.get("removed_transactions")
                delete_transactions.delay(item_id, removed_transactions)

            else:
                new_transactions = request_data.get("new_transactions")
                fetch_transactions.delay(item_id, new_transactions)
    except:
        pass
    return Response({"detail": "Webhook received"}, status=status.HTTP_202_ACCEPTED)


# This is just to trigger a fetch task
@api_view(["POST"])
def testCelery(request):
    print("Starting Celery Async Task...")
    try:
        item_id = Item.objects.all()[0].item_id
        fetch_accounts_transactions.delay(item_id)
        return Response(
            data={
                "detail": "Successfully started the task. Check celery logs for details"
            },
            status=status.HTTP_200_OK,
        )
    except:
        return Response(
            data={
                "detail": "Unable to start celery task, make sure atleast one user has linked his account"
            },
            status=status.HTTP_428_PRECONDITION_REQUIRED,
        )
