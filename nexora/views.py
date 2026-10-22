from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib import messages
from .models import Transaction



def home(request):
    transaction=Transaction.objects.all().order_by('-id')
    context={
        "transactions": transaction
    }
    template=loader.get_template("home.html")
    return HttpResponse(template.render(context,request))


def dashboard(request):
    transaction=Transaction.objects.all().order_by('-id')[:5]  # Get the 5 most recent transactions
    context={
        "recent_transactions": transaction
    }
    template= loader.get_template('dashboard.html')
    return HttpResponse(template.render(context, request))
    