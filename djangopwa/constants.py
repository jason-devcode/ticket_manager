from django.db import models


MAX_TELEPHONE_DIGITS: int = 10
MAX_WHATSAPP_DIGITS: int = 10


MAX_TIME_DAYS_RESERVATION_TICKET: int = 9

# For testing model validation
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 10  # 10mb

class TicketState(models.IntegerChoices):
    """
    Enumeration for the different states a ticket can be in.

    Attributes
    ----------
    AVAILABLE : int
        The ticket is available for purchase.
    RESERVED : int
        The ticket is reserved but not yet purchased.
    PURCHASED : int
        The ticket has been purchased.
    """

    AVAILABLE = 1, "Disponible"
    RESERVED = 2, "Reservada"
    PURCHASED = 3, "Comprada"


BANK_NAMES = [
    ("NEQUI", "Nequi"),
    ("BANCOLOMBIA", "Bancolombia"),
    ("DAVIPLATA", "Daviplata"),
]
