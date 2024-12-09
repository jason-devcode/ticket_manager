from django.utils.dateparse import parse_date

from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q as ComplexQueryFilter


from djangopwa import models


def parse_dates(dates):
    """
    Parse a list of date strings into datetime objects.

    Args:
        dates (list): A list of date strings.

    Returns:
        list: A list of parsed datetime objects.
    """
    return [parse_date(date_str) for date_str in dates if parse_date(date_str)]


def adjust_date_range(dates):
    """
    Adjust a list of dates to include the full day range with timezone awareness.

    Args:
        dates (list): A list of datetime objects.

    Returns:
        list: A list of tuples containing start and end datetime objects for each day.
    """
    adjusted_dates = []
    for date in dates:
        start_date = timezone.make_aware(datetime(date.year, date.month, date.day))
        end_date = start_date + timedelta(days=1)
        adjusted_dates.append((start_date, end_date))
    return adjusted_dates


def build_complex_queries_filter_by_dates(dates) -> ComplexQueryFilter:
    """
    Build a complex query filter for filtering by date range.

    Args:
        dates (list): A list of datetime objects.

    Returns:
        ComplexQueryFilter: A complex query filter for the specified date ranges.
    """

    queries = ComplexQueryFilter()
    for start_date, end_date in adjust_date_range(dates):
        queries |= ComplexQueryFilter(date__gte=start_date, date__lt=end_date)

    return queries


def filter_model_by_dates(seller_id, dates):
    """
    Filter the Payment model by seller ID and date range.

    Args:
        seller_id (int): The ID of the seller.
        dates (list): A list of datetime objects.

    Returns:
        QuerySet: A queryset of filtered Payment objects.
    """
    if not dates:
        return models.Payment.objects.none()
    queries = build_complex_queries_filter_by_dates(dates)
    return models.Payment.objects.filter(seller_id=seller_id).filter(queries)


def generate_balance(payments):
    """
    Generate a balance summary from a list of payments.

    Args:
        payments (list): A list of dictionaries, where each dictionary represents a payment.
            Each payment dictionary should contain:
                - client_id (int): The ID of the client.
                - amount (float): The amount of the payment.
                - date (datetime.date): The date of the payment.

    Returns:
        dict: A dictionary representing the balance summary. The dictionary contains:
            - "total": A dictionary with the total amount of all payments.
            - Each client_id as a key, where the value is a dictionary containing:
                - client_id (int): The ID of the client.
                - ticket_number (str): The ticket number of the client, zero-padded to 4 digits.
                - total_amount (float): The total amount of payments for the client.
                - last_payment_date (datetime.date): The date of the last payment for the client.
    """
    balance = {"total": {"amount": 0}}

    for payment in payments:
        client_id = payment.get("client_id")
        amount = payment.get("amount")
        date = payment.get("date")

        balance["total"]["amount"] += amount

        if client_id in balance:
            balance[client_id]["total_amount"] += amount
            last_payment_date = balance.get(client_id).get("last_payment_date")
            if date > last_payment_date:
                balance[client_id]["last_payment_date"] = date
        else:
            ticket_number = models.ClientInfo.objects.get(
                id=client_id
            ).ticket_number.number

            balance[client_id] = {
                "client_id": client_id,
                "ticket_number": f"{str(ticket_number).zfill(4)}",
                "total_amount": amount,
                "last_payment_date": date,
            }

    return balance


from django.core.serializers.json import DjangoJSONEncoder
import json


def serialize_seller_bill_json(bill):
    """
    Serialize a SellerBill instance into JSON format, including all seller data and payment balances.

    Args:
        bill (models.SellerBill): The SellerBill instance to serialize.

    Returns:
        str: JSON representation of the SellerBill instance with all seller data and payment balances.
    """
    # Fetch all seller data fields
    seller_data = {
        "seller_id": bill.seller.id,
        "first_name": bill.seller.first_name,
        "last_name": bill.seller.last_name,
        "document_number": bill.seller.document_number,
        "city_residence": bill.seller.city_residence,
        "whatsapp": bill.seller.whatsapp,
    }

    # Fetch related payment balances
    payment_balances = list(
        bill.clientticketpaymentbalance_set.all().values(
            "client_id", "ticket_number", "total_amount", "last_payment_date"
        )
    )

    # Serialize SellerBill instance
    data = {
        "bill_id": bill.id,
        "generation_date": bill.generation_date,
        "seller": seller_data,
        "total_amount": bill.total_amount,
        "payment_balances": payment_balances,
    }

    return data


def generate_seller_bill(seller_id, payments):
    """
    Generate a seller's bill and print the payment balances.

    Args:
        seller_id (int): The ID of the seller.
        payments (list): A list of dictionaries, where each dictionary represents a payment.
            Each payment dictionary should contain:
                - client_id (int): The ID of the client.
                - amount (float): The amount of the payment.
                - date (datetime.date): The date of the payment.
    """
    balance = payments

    bill = models.SellerBill(
        generation_date=timezone.now(),
        seller_id=seller_id,
        total_amount=balance["total"]["amount"],
    )
    bill.save()
    # Save client ticket payment balances
    for client_id, details in balance.items():
        if client_id != "total":
            models.ClientTicketPaymentBalance.objects.create(
                seller_bill=bill,
                client_id=client_id,
                ticket_number=details["ticket_number"],
                total_amount=details["total_amount"],
                last_payment_date=details["last_payment_date"],
            )

    return bill


def get_payments_by_dates(seller_id, dates):
    """
    Get payments by seller ID and date range.

    Args:
        seller_id (int): The ID of the seller.
        dates (list): A list of datetime objects.

    Returns:
        list: A list of payments filtered by the specified dates.
    """
    payments = filter_model_by_dates(seller_id=seller_id, dates=dates).values()
    return list(payments)
