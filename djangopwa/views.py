import random
import string
import requests

from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator

from djangopwa import constants
from djangopwa.constants import TicketState
from djangopwa.payment_balance import (
    parse_dates,
    get_payments_by_dates,
    generate_balance,
    generate_seller_bill,
    serialize_seller_bill_json,
)

import json

from lottery.wompi import wompi
from . import models


def check_user_active(user):
    return user.is_authenticated and user.is_active

def get_ticket_state(request):
    lottery_id = request.GET.get("lottery_id", "")
    ticket_number = request.GET.get("ticket_number", "")
    lottery = models.Lottery.objects.filter(id=lottery_id).first()
    ticket = models.Ticket.objects.filter(
        lottery=lottery, number=ticket_number).first()
    return JsonResponse({"ticket_state": ticket.state == TicketState.AVAILABLE})


def get_request_body(request):
    try:
        body_unicode = request.body.decode("utf-8")
        return json.loads(body_unicode)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def build_json_response(data, status="success", message=""):
    return JsonResponse({"status": status, "data": data, "message": message})


@user_passes_test(check_user_active)
def get_seller_balance_payment_list(request, seller_id):
    dates = get_request_body(request).get("dates")
    parsed_dates = parse_dates(dates)
    payments = get_payments_by_dates(seller_id, parsed_dates)
    balance = generate_balance(payments=payments)
    return build_json_response(data=balance)


@user_passes_test(check_user_active)
def generate_seller_bill_endpoint(request, seller_id):
    """
    Endpoint to generate the seller's bill.

    Args:
        request (HttpRequest): The HTTP request.
        seller_id (int): The ID of the seller.

    Returns:
        JsonResponse: The JSON response with the seller's bill details.
    """
    request_data = get_request_body(request)
    if not request_data:
        return build_json_response(
            data={}, status="error", message="Invalid JSON data."
        )

    payments = request_data.get("payments")
    if not payments:
        return build_json_response(
            data={}, status="error", message="Payments are required."
        )

    bill = generate_seller_bill(seller_id, payments)
    serialized_bill = serialize_seller_bill_json(bill)

    return build_json_response(
        data={"bill": serialized_bill}, message="Bill generated successfully."
    )


def generate_random_string(length=12):
    letters_and_digits = string.ascii_letters + string.digits
    return "".join(random.choice(letters_and_digits) for i in range(length))


@user_passes_test(check_user_active)
def verify_ticket_purchase(request, client_id):
    message = ""
    try:
        client = models.ClientInfo.objects.filter(id=client_id).first()

        ticket = client.ticket_number
        ticket.state = TicketState.PURCHASED

        reserved_ticket = models.TicketReserved.objects.filter(ticket=ticket).first()
        pending_purchase = models.TicketPendingPurchase.objects.filter(
            ticket=ticket).first()

        purchase_ticket = models.TicketPurchased.objects.filter(
            ticket=ticket,
            client=client,
            purchase_reference=client.purchase_reference
        ).first()
        
        if purchase_ticket is None:
            purchase_ticket = models.TicketPurchased(
                ticket=ticket,
                client=client,
                purchase_reference=client.purchase_reference
            )
            if purchase_ticket:
                purchase_ticket.save()
        
        if pending_purchase:
            pending_purchase.delete()
        
        if reserved_ticket:
            reserved_ticket.delete()

        if ticket:
            ticket.save()

        message = "Ticket purchase verified successfully."
    except Exception as e:
        message = str(e)

    return build_json_response(data={}, message=message)


def get_client_side_whatsapp(request):
    whatsapp = models.Whatsapp.objects.order_by("-id").first()

    if whatsapp is None:
        response_data = {"whatsapp": ""}
    else:
        response_data = {
            "whatsapp": whatsapp.whatsapp,
        }

    return build_json_response(data=response_data, message="")


class PaymentType:
    BONO1 = 1
    BONO2 = 2
    BONO3 = 3
    TOTAL = 4


def get_bono_client_bill_data(client: models.ClientInfo, billType):
    ticket_number = client.ticket_number

    payment_type = f"BONO{billType}"

    payment: models.Payment | None = models.Payment.objects.filter(
        client=client, payment_type=payment_type
    ).first()

    if payment is None:
        return None

    try:        
        templates = models.BillImage.objects.filter(
            lottery=client.ticket_number.lottery
        )
        
        bill_ticket_template_image_url = templates.get(image_type="TICKET_TEMPLATE").image.url
        bill_certificate_template_image_url = templates.get(image_type="CERTIFICATE_TEMPLATE").image.url
        
    except models.BillImage.DoesNotExist:
        bill_ticket_template_image_url = ""
        bill_certificate_template_image_url = ""
        
    payment_balance = calculate_client_balance(client)
    amount_to_pay = client.lottery_to_buy.price_per_ticket - payment_balance
    
    return {
        "number_bill": client.id + billType,
        "ticket_template": bill_ticket_template_image_url,
        "generation_date": timezone.now(),
        "individual_bill": True,
        "type_payment": f"BONO {billType}",
        "ticket_number": f"{ticket_number.number:04d}",
        "purchase_reference": client.purchase_reference,
        "client": {
            "id": client.id,
            "name": client.name,
            "lastname": client.lastname,
            "document": client.document_number,
            "telephone": client.telephone,
            "whatsapp": client.whatsapp,
            "balance": f"{payment.amount:,.0f}".replace(',', '.'),
            "amount_to_pay": f"{amount_to_pay:,.0f}".replace(',', '.'),
            "city": client.city,
            "seller_name_lastname": f"{client.seller.first_name} {client.seller.last_name}"
        },
    }


def get_total_payment_client_bill_data(client: models.ClientInfo, billType):
    try:        
        templates = models.BillImage.objects.filter(
            lottery=client.ticket_number.lottery
        )
        
        bill_ticket_template_image_url = templates.get(image_type="TICKET_TEMPLATE").image.url
        bill_certificate_template_image_url = templates.get(image_type="CERTIFICATE_TEMPLATE").image.url
        
    except models.BillImage.DoesNotExist:
        bill_ticket_template_image_url = ""
        bill_certificate_template_image_url = ""
        
    payment_balance = calculate_client_balance(client)
    amount_to_pay = client.lottery_to_buy.price_per_ticket - payment_balance

    return {
        "number_bill": f"{client.id}{billType}",
        "ticket_template": bill_ticket_template_image_url,
        "certificate_template": bill_certificate_template_image_url,
        "generation_date": timezone.now(),
        "individual_bill": True,
        "type_payment": "TOTAL",
        "ticket_number": f"{client.ticket_number.number:04d}",
        "purchase_reference": client.purchase_reference,
        "client": {
            "id": client.id,
            "name": client.name,
            "lastname": client.lastname,
            "document": client.document_number,
            "telephone": client.telephone,
            "whatsapp": client.whatsapp,
            "balance": f"{payment_balance:,.0f}".replace(',', '.'),
            "amount_to_pay": f"{amount_to_pay:,.0f}".replace(',', '.'),
            "city": client.city,
            "seller_name_lastname": f"{client.seller.first_name} {client.seller.last_name}"
        },
    }


@user_passes_test(check_user_active)
def get_client_bill_data(request, clientId, billType):

    client = models.ClientInfo.objects.get(id=clientId)

    data = {"bill_data": None}

    if client is None:
        return data

    if billType < PaymentType.TOTAL:
        bill_data = get_bono_client_bill_data(client, billType)
    elif billType == PaymentType.TOTAL:
        bill_data = get_total_payment_client_bill_data(client, billType)

    data["bill_data"] = bill_data

    return JsonResponse(data=data)


def mask_after_third_character(string):
    if len(string) <= 3:
        return string
    else:
        return string[:3] + "*" * (len(string) - 3)


def mask_except_last_three_characters(string):
    if len(string) <= 3:
        return string
    else:
        return "*" * (len(string) - 3) + string[-3:]


def get_ticket_info(request, lottery_id, ticket_number):

    lottery = models.Lottery.objects.get(id=lottery_id)
    ticket = models.Ticket.objects.filter(
        lottery=lottery, number=ticket_number).first()

    data = {"isAvailable": False}

    if ticket.state == constants.TicketState.AVAILABLE:
        data["isAvailable"] = True
        return JsonResponse(data)

    client = None

    data["ticket_state"] = ticket.state

    if ticket.state == constants.TicketState.PURCHASED:
        ticket_purchased = models.TicketPurchased.objects.get(ticket=ticket)
        client = ticket_purchased.client
    if ticket.state == constants.TicketState.RESERVED:
        ticket_reserved = models.TicketReserved.objects.get(ticket=ticket)
        client = ticket_reserved.client
    if client:
        payments = models.Payment.objects.filter(client=client)

        payment_count = payments.count()

        total_payment = 0
        for payment in payments:
            total_payment += payment.amount

        client_context = {
            "name_and_lastname": mask_after_third_character(client.name)
            + " "
            + mask_after_third_character(client.lastname),
            "document_number": mask_except_last_three_characters(
                str(client.document_number)
            ),
            "payment_count": payment_count,
            "total_payment": total_payment,
        }
        data["client"] = client_context
    return JsonResponse(data)


def calculate_client_balance(client):
    payments = models.Payment.objects.filter(client=client)
    payment_balance = 0
    for payment in payments:
        payment_balance += payment.amount
    return payment_balance


@user_passes_test(check_user_active)
def get_ticket_png_data(request, client_id):
    data = {"success": False, "message": ""}

    client = models.ClientInfo.objects.get(id=client_id)

    if client is None:
        data["message"] = f"Could not get client with id {client_id}"
        return JsonResponse(data)

    client_balance = calculate_client_balance(client)
    ticket_price = client.lottery_to_buy.price_per_ticket
    amount_to_pay = ticket_price - client_balance

    data["ticket_png_data"] = {
        "ticket_number": f"{client.ticket_number.number:04}",
        "client_name_lastname": f"{client.name} {client.lastname}",
        "client_whatsapp": f"https://wa.me/{client.whatsapp}",
        "seller_name_lastname": f"{client.seller.first_name} {client.seller.last_name}",
        "date_generation": timezone.now(),
        "balance": f"{client_balance:,.0f}".replace(',', '.'),
        "amount_to_pay": f"{amount_to_pay:,.0f}".replace(',', '.')
    }

    data["success"] = True

    return JsonResponse(data)


@user_passes_test(check_user_active)
def decline_ticket(request, client_id):
    data = {"success": False}

    try:
        client = models.ClientInfo.objects.get(id=client_id)
        ticket = client.ticket_number
        if ticket.state != TicketState.AVAILABLE:
            ticket.state = TicketState.AVAILABLE
            ticket.save()
        client.delete()
        data["success"] = True
    except models.ClientInfo.DoesNotExist:
        data["error"] = "Client not found"
    except models.Ticket.DoesNotExist:
        data["error"] = "Ticket not found"
    except Exception as e:
        data["error"] = str(e)

    return JsonResponse(data)


def get_tickets_to_assign(request):
    lottery_id = request.GET.get('lottery_id')
    tickets_selected = request.GET.get('tickets_selected', '')

    if lottery_id:
        # Fetch available tickets and exclude already assigned ones
        tickets = models.Ticket.objects.filter(
            lottery_id=lottery_id,
        )
    else:
        tickets = models.Ticket.objects.none()

    # Prepare the response data
    data = [{'id': ticket.id, 'number': f"{ticket.number:04}"} for ticket in tickets]
    return JsonResponse(data, safe=False)
