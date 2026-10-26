from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator    #prevents amounts below 0.01. So basically thats the lowest decomal you can have   

class Transaction(models.Model):

    class TransactionType(models.TextChoices):
        income= "income", "Income"
        expense= "expense", "Expense"
    #This is for us to know the Type of Transaction we wanna make, be it an Income or an Expense

    class Currency(models.TextChoices):
        #We can have people usimg different currencies but our default currency will be Naria
        NGN="NGN", "Nigeria Naria"
        USD="USD", "US Dollar"
        GBP="GBP", "British Pound"
        EUR="EUR", "Euro"
        #This are all the currencies we wanna use for now. If we end up turning this project into something bigger we can add more currencies

    class Category(models.TextChoices):
        #This is for us to know the Category of Transaction we wanna make, be it an Income or an Expense
        food="food", "Food"
        transport="transport", "Transport"
        bills="bills","Bills"
        shopping="shopping", "Shopping"
        education="education", "Education"
        other="Other", "Other"

        #foreign Key establishes a relationship between the transaction class and its owner
    user=models.ForeignKey(
        settings.AUTH_USER_MODEL,#it reference to Django configured user model
        on_delete=models.CASCADE,#delete the users transaction when the user is deleted
        related_name="transacationa"#Let's user access all the transactions by doing the user.transaction.all()
        )
    title=models.CharField(max_length=200)

    amount=models.DecimalField(
        max_digits=12,
        decimal_places=2,#0.01
        validators=[MinValueValidator(0.01)]#Rejects 0 and negative numbers during validation
    )

    transaction_type=models.CharField(
        max_length=10,
        choices=TransactionType.choices
    )

    currency=models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.NGN
    )

    category=models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.other
    )

    description = models.TextField(blank=True)

    created=models.DateTimeField(auto_now_add=True)#What this does is that it records the time the transaction was initiated

    date=models.DateField(default=timezone.localdate)#What this does is that it gives us the exact date the tansation was initated

    updated=models.DateTimeField(auto_now=True)#When the recirds was last saved

    class Meta():
        ordering=['-date', '-created']

    def __str__(self):
        return f"{self.title} -- {self.amount} {self.currency}"#Defines how the transaction is represnted as a text
