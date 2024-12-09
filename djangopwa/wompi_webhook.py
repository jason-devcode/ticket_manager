from . import models
import hashlib
import logging

from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime

import json

from lottery.wompi import wompi

logger = logging.getLogger(__name__)


def generate_sha256_hash(input_string):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input_string.encode('utf-8'))
    return sha256_hash.hexdigest()


def get_nested_value(data, key_path):
    keys = key_path.split('.')
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key)
        else:
            return None
    return data


def validate_signature_hash256(data):
    try:
        signature = data.get("signature", {})
        checksum = signature.get("checksum")
        properties = signature.get("properties", [])
        timestamp = data.get("timestamp")

        if not checksum or not properties or timestamp is None:
            logger.warning(
                "Request body is missing required fields for signature validation")
            return False

        transaction_data = data.get("data", {})

        properties_concat = ""
        for property in properties:
            property_value = get_nested_value(transaction_data, property)
            if property_value is None:
                logger.warning(
                    "Property '%s' not found in transaction data", property)
                return False
            properties_concat += str(property_value)

        properties_concat += str(timestamp)
        properties_concat += wompi.credentials.events_key

        generated_checksum_hash256 = generate_sha256_hash(properties_concat)

        if generated_checksum_hash256 != checksum:
            logger.warning("Checksum validation failed: expected '%s', got '%s'",
                           checksum, generated_checksum_hash256)
            return False

        return True
    except Exception as e:
        logger.error(
            "An error occurred during signature validation: %s", str(e))
        return False

from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP

def transaction_updated_event(data):
    if not validate_signature_hash256(data):
        logger.error("Transaction update event failed due to invalid signature")
        return {"message": "ERROR: Could not validate signature"}

    transaction_data = data["data"]["transaction"]

    if not all(key in transaction_data for key in ["id", "status", "reference", "finalized_at", "payment_method", "amount_in_cents"]):
        logger.error("Incomplete transaction data")
        return {"message": "ERROR: Incomplete transaction data"}

    transaction_id = transaction_data["id"]
    transaction_status = transaction_data["status"]
    purchase_reference = transaction_data["reference"]

    if transaction_status != "APPROVED":
        return {"message": "Transaction declined"}

    clients = models.ClientInfo.objects.filter(purchase_reference=purchase_reference)

    if not clients.exists():
        return {"message": "No clients found for the given purchase reference"}

    finalized_at_datetime = parse_datetime(transaction_data["finalized_at"])
    payment_method = transaction_data["payment_method"]["type"]
    amount_in_cents = transaction_data["amount_in_cents"]
    amount_in_pesos = Decimal(amount_in_cents) / 100

    num_clients = len(clients)
    
    if num_clients == 0:
        logger.error("No clients found for the given purchase reference")
        return {"message": "No clients to distribute the payment"}

    # Calculate base amount per client
    base_amount_per_client = amount_in_pesos / num_clients
    base_amount_per_client = base_amount_per_client.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

    # Calculate total distributed with base amount
    total_distributed = base_amount_per_client * num_clients

    # Calculate the difference and distribute it
    difference = amount_in_pesos - total_distributed

    # Allocate the difference to the last client
    for index, client in enumerate(clients):
        if index == num_clients - 1:  # Last client
            payment_amount = base_amount_per_client + difference
        else:
            payment_amount = base_amount_per_client

        payment = models.Payment(
            seller=client.seller,
            client=client,
            date=finalized_at_datetime,
            payment_type="BONO1",
            transaction_id=transaction_id,
            purchase_reference=purchase_reference,
            payment_method=payment_method,
            amount=payment_amount
        )
        payment.save()

    return {"message": "Transaction updated successfully"}


def process_event(data):
    if "event" in data and data["event"] == "transaction.updated":
        return transaction_updated_event(data)
    return {"message": "No valid event found"}


@csrf_exempt
def wompi_webhook(request):
    if request.method != "POST":
        logger.warning("Received a non-POST request: %s", request.method)
        return HttpResponseBadRequest("Only POST requests are allowed.")

    logger.info("Received a POST request")

    try:
        data = json.loads(request.body)

        response = process_event(data)
        if isinstance(response, dict) and "message" in response:
            return JsonResponse(response)

        logger.warning("No valid response from process_event")
        return JsonResponse({"message": "Event processed but no valid response"}, status=500)

    except json.JSONDecodeError:
        logger.error("Error decoding JSON: %s", request.body)
        return HttpResponseBadRequest("Invalid JSON format.")

    except Exception as e:
        logger.error("An unexpected error occurred: %s", str(e))
        return JsonResponse({"message": "An unexpected error occurred"}, status=500)
