from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Transaction


class ConfirmTransactionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.force_login(self.user)
        self.transaction_data = {
            "title": "Groceries",
            "amount": "25.50",
            "transaction_type": "expense",
            "currency": "NGN",
            "category": "food",
            "description": "Weekly shopping",
        }

    def test_transaction_is_saved_once_after_confirmation(self):
        preview_response = self.client.post(
            reverse("confirm"), self.transaction_data
        )
        self.assertEqual(preview_response.status_code, 200)
        self.assertContains(preview_response, 'type="hidden" name="confirm" value="yes"')
        self.assertEqual(Transaction.objects.count(), 0)

        confirmation_token = self.client.session["pending_transaction_confirmation"]
        confirm_response = self.client.post(
            reverse("confirm"),
            {
                **self.transaction_data,
                "confirm": "yes",
                "confirmation_token": confirmation_token,
            },
        )
        self.assertRedirects(confirm_response, reverse("dashboard"))
        self.assertEqual(Transaction.objects.count(), 1)

        repeated_response = self.client.post(
            reverse("confirm"),
            {
                **self.transaction_data,
                "confirm": "yes",
                "confirmation_token": confirmation_token,
            },
        )
        self.assertRedirects(repeated_response, reverse("dashboard"))
        self.assertEqual(Transaction.objects.count(), 1)

    def test_invalid_transaction_is_not_saved(self):
        invalid_data = {**self.transaction_data, "amount": "-1"}

        response = self.client.post(reverse("confirm"), invalid_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("add_transaction"))
        self.assertEqual(Transaction.objects.count(), 0)

    def test_non_finite_amount_is_not_saved(self):
        invalid_data = {**self.transaction_data, "amount": "NaN"}

        response = self.client.post(reverse("confirm"), invalid_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("add_transaction"))
        self.assertEqual(Transaction.objects.count(), 0)


class ReportsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="reportuser", password="password")
        self.client.force_login(self.user)

    def test_reports_include_currency_totals_monthly_cashflow_and_categories(self):
        Transaction.objects.create(
            user=self.user,
            title="Salary",
            amount="2500.00",
            transaction_type="income",
            currency="NGN",
            category="other",
        )
        Transaction.objects.create(
            user=self.user,
            title="Groceries",
            amount="150.00",
            transaction_type="expense",
            currency="NGN",
            category="food",
        )

        response = self.client.get(reverse("reports"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="cashflow-chart"')
        self.assertContains(response, 'id="category-chart"')
        self.assertEqual(response.context["report_data"]["NGN"]["balance"], 2350)
        chart_data = response.context["chart_data"]["NGN"]
        self.assertEqual(len(chart_data["months"]), 6)
        self.assertEqual(Decimal(chart_data["income"][-1]), Decimal("2500.00"))
        self.assertEqual(Decimal(chart_data["expenses"][-1]), Decimal("150.00"))
        self.assertEqual(len(chart_data["categories"]), 1)
        self.assertEqual(chart_data["categories"][0]["name"], "Food")
        self.assertEqual(
            Decimal(chart_data["categories"][0]["value"]), Decimal("150.00")
        )

    def test_reports_only_include_the_logged_in_users_transactions(self):
        other_user = User.objects.create_user(username="otheruser", password="password")
        Transaction.objects.create(
            user=other_user,
            title="Private income",
            amount="900.00",
            transaction_type="income",
            currency="USD",
            category="other",
        )

        response = self.client.get(reverse("reports"))

        self.assertEqual(response.context["report_data"]["USD"]["income"], 0)
        self.assertEqual(response.context["chart_data"]["USD"]["income"], ["0"] * 6)


class TransactionsPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="transactionuser", password="test-pass")
        self.client.force_login(self.user)

    def test_transactions_page_renders_search_bar(self):
        response = self.client.get(reverse("transactions"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="transaction-search"')
        self.assertContains(response, 'class="transactions-table"')
