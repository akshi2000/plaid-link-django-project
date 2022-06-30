from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("signup/", views.signupView, name="signupapi"),
    path("login/", views.loginView, name="loginapi"),
    path("logout/", views.logoutView, name="logoutapi"),
    path("getlinktoken/", views.getLinkToken, name="getlinktoken"),
    path("gettransactions/", views.getTransaction, name="gettransactions"),
    path("getaccesstoken/", views.getAccessToken, name="getaccesstoken"),
    path("getaccountdata/", views.getAccountData, name="getaccountdata"),
    path("webhook/", views.webhook, name="webhook"),
    # celery task test
    path("triggercelery/", views.testCelery, name="testCelery"),
]
