from datetime import date
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum
from django.shortcuts import redirect
from django.contrib import messages
from .models import Transaction


@login_required
def dashboard(request):
    transaction=Transaction.objects.filter(user=request.user).order_by('-id')[:5]  # Get the 5 most recent transactions

    currencies = ['NGN', 'USD', 'GBP', 'EUR']
    balances = {}
    total={}
    expenses={}
    for currency in currencies:
         
         #to calculate the total income
         total_income=Transaction.objects.filter(
              user=request.user,
              transaction_type="income",
              currency=currency
         ).aggregate(total=Sum('amount'))["total"] or 0

         #to calculate the total expense
         total_expense=Transaction.objects.filter(
              user=request.user,
              transaction_type="expense",
              currency=currency
         ).aggregate(total=Sum('amount'))["total"] or 0

         #total income for each currency
         if currency == 'NGN':
             total['NGN'] = total_income

         elif currency == 'USD':
             total['USD'] = total_income

         elif currency == 'GBP':
             total['GBP'] = total_income

         elif currency == 'EUR':
                total['EUR'] = total_income

         #total expense for each currency       
         if currency == 'NGN':
             expenses['NGN'] = total_expense

         elif currency == 'USD':
             expenses['USD'] = total_expense

         elif currency == 'GBP':
             expenses['GBP'] = total_expense

         elif currency == 'EUR':
             expenses['EUR'] = total_expense

         #balance    
         if currency == 'NGN':
            balances['NGN'] = total_income - total_expense

         elif currency == 'USD':
            balances['USD'] = total_income - total_expense

         elif currency == 'GBP':
            balances['GBP'] = total_income - total_expense

         elif currency == 'EUR':
            balances['EUR'] = total_income - total_expense

         else:
            balances[currency] = 0
    context={
        "recent_transactions": transaction,
        "balances": balances,
        "total": total,
        "expenses": expenses
    }
    template= loader.get_template('dashboard.html')
    return HttpResponse(template.render(context, request))

@login_required
def add_transaction(request):
    
        context = {
         "currency": Transaction.Currency.choices,
        "category": Transaction.Category.choices,
            
        }
        template= loader.get_template('transaction_form.html')
        return HttpResponse(template.render(context, request))

    

@login_required
def confirm_transaction(request):
    if request.method != "POST":
        return redirect("add_transaction")

    title = request.POST.get("title", "").strip()
    amount = request.POST.get("amount", "")
    transaction_type = request.POST.get("transaction_type", "")
    currency = request.POST.get("currency", "")
    category = request.POST.get("category", "")
    description = request.POST.get("description", "")

    try:
        amount = Decimal(amount)
    except (InvalidOperation, TypeError):
        messages.error(request, "Enter a Valid Number")
        return redirect('add_transaction')

    if not amount.is_finite():
        messages.error(request, "Enter a Valid Number")
        return redirect("add_transaction")

    transaction = Transaction(
        user=request.user,
        title=title,
        amount=amount,
        transaction_type=transaction_type,
        category=category,
        description=description,
        currency=currency,
    )

    try:
        transaction.full_clean()
        #checks if the transaction is valid according to the model's validation rules
    except ValidationError:
        messages.error(request, "Please enter valid transaction details.")
        return redirect("add_transaction")

    if request.POST.get("confirm") == "yes":
        confirmation_token = request.POST.get("confirmation_token")
        #Generate a unique token when displaying the confirmation page.
        if confirmation_token != request.session.get("pending_transaction_confirmation"):
            messages.error(request, "This transaction confirmation has already been used.")
            return redirect("dashboard")
        transaction.save()

        del request.session["pending_transaction_confirmation"]
        return redirect("dashboard")
        

    confirmation_token = uuid4().hex
    request.session["pending_transaction_confirmation"] = confirmation_token
    context = {
        "title": title,
        "amount": amount,
        "transaction_type": transaction_type,
        "currency": currency,
        "category": category,
        "description": description,
        "confirmation_token": confirmation_token,
    }
    template = loader.get_template("confirmation.html")
    return HttpResponse(template.render(context, request))


def login_Page(request):
    if request.method == "POST":
        username=request.POST.get("username", '').strip()
        password=request.POST.get("password", '')

        user=authenticate(
              request,
              username=username, 
              password=password
              )
        #Checks if the username and password match a user in the database. If they do, it returns the user object; otherwise, it returns None.

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        #If the user is None, it means the authentication failed, and we display an error message and redirect back to the login page.
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')
    template= loader.get_template("login.html")
    context={

    }
    return HttpResponse(template.render(context, request))

def sign_Up(request):
    if request.method=="POST":
        username=request.POST.get("username", '').strip()
        password1=request.POST.get("password1", '')
        password2=request.POST.get("password2", '')

        if password1 != password2:
            messages.error(request, "The password does not match")
            return redirect('sign_up')

        if not username or not password1 or not password2:
            messages.error(request, "Please fill in all fields")
            return redirect('sign_up')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('sign_up')
        
        if password1 == password2:
            user=User.objects.create_user(
                username=username,
                password=password1,
            )
            #create_user() hashes the password so Django can authenticate the user securely.
            login(request, user)
            messages.success(request, "Account created successfully")
            return redirect('dashboard')
            

    template= loader.get_template("sign_up.html")
    context={

        }
    return HttpResponse(template.render(context, request))


def logoutPage(request):
    logout(request)
    messages.success(request, "You have logged out successfully.")
    return redirect("login")

@login_required
def transactions(request):
    user_transactions = Transaction.objects.filter(
        user=request.user
    ).order_by("-id")

    return render(request, "transactions.html", {
        "transactions": user_transactions
    })


@login_required
def reports(request):
    currencies = ["NGN", "USD", "GBP", "EUR"]
    today = timezone.localdate()
    month_starts = []
    for offset in range(5, -1, -1):
        month_index = today.year * 12 + today.month - 1 - offset
        month_starts.append(date(month_index // 12, month_index % 12 + 1, 1))
    month_labels = [month.strftime("%b") for month in month_starts]

    user_transactions = Transaction.objects.filter(user=request.user)
    totals = {
        (row["currency"], row["transaction_type"]): row["total"]
        for row in user_transactions.values("currency", "transaction_type").annotate(
            total=Sum("amount")
        )
    }
    monthly_totals = {}
    for row in (
        user_transactions.filter(date__gte=month_starts[0], date__lte=today)
        .annotate(month=TruncMonth("date"))
        .values("currency", "transaction_type", "month")
        .annotate(total=Sum("amount"))
    ):
        key = (row["currency"], row["transaction_type"], row["month"].strftime("%Y-%m"))
        monthly_totals[key] = row["total"]

    category_totals = {
        (row["currency"], row["category"]): row["total"]
        for row in user_transactions.filter(transaction_type="expense")
        .values("currency", "category")
        .annotate(total=Sum("amount"))
    }

    report_data = {}
    chart_data = {}
    for currency in currencies:
        income = totals.get((currency, "income"), Decimal("0"))
        expenses = totals.get((currency, "expense"), Decimal("0"))
        report_data[currency] = {
            "income": income,
            "expenses": expenses,
            "balance": income - expenses,
        }
        chart_data[currency] = {
            "months": month_labels,
            "income": [
                str(monthly_totals.get((currency, "income", month.strftime("%Y-%m")), 0))
                for month in month_starts
            ],
            "expenses": [
                str(monthly_totals.get((currency, "expense", month.strftime("%Y-%m")), 0))
                for month in month_starts
            ],
            "categories": [
                {
                    "name": label,
                    "value": str(category_totals[(currency, value)]),
                }
                for value, label in Transaction.Category.choices
                if category_totals.get((currency, value), 0) > 0
            ],
        }

    return render(request, "reports.html", {
        "report_data": report_data,
        "chart_data": chart_data,
    })