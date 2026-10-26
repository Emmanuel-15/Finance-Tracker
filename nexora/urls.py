from . import views
from django.urls import path

urlpatterns=[
    path("dashboard/", views.dashboard, name="dashboard"),

    path("add-transaction/", views.add_transaction, name="add_transaction"),

    path("confirm/", views.confirm_transaction, name="confirm"),

    path("", views.sign_Up, name="sign_up"),

    path("login/", views.login_Page, name="login"),

    path("logout/", views.logoutPage, name="logout"),

    path("transactions/", views.transactions, name="transactions"),

    path("reports/", views.reports, name="reports"),

]