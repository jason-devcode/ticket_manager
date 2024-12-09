from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from . import constants

from cloudinary.models import CloudinaryField
from djangopwa.cloudinary import file_validation


class User(AbstractUser):
    class Meta:
        verbose_name = "Vendedor"
        verbose_name_plural = "Vendedores"

    ROL_CHOICES = (
        ("VENDEDOR", "Vendedor"),
        ("SUPERADMIN", "Super Admin"),
    )
    role = models.CharField(
        verbose_name="Rol", max_length=20, choices=ROL_CHOICES)
    document_number = models.CharField(
        verbose_name="Número de documento", max_length=50
    )
    city_residence = models.CharField(verbose_name="Ciudad", max_length=32)
    whatsapp = models.CharField(max_length=15)
    is_staff = models.BooleanField(
        default=True,
        help_text="Designates whether the user can log into this admin site.",
        verbose_name="staff status",
    )


class PaymentMethod(models.Model):
    name = models.CharField(max_length=32)

    class Meta:
        verbose_name = "Metodo de pago"
        verbose_name_plural = "Metodos de pago"

    def __str__(self):
        return self.name


def get_default_seller():
    return User.objects.get(id=1)


class ClientInfo(models.Model):
    lottery_to_buy = models.ForeignKey(
        "Lottery",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Rifa a comprar",
    )

    ticket_number = models.ForeignKey(
        "Ticket",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Numero de rifa",
    )

    name = models.CharField(verbose_name="Nombres", max_length=32)
    lastname = models.CharField(verbose_name="Apellidos", max_length=32)
    whatsapp = models.IntegerField()
    document_number = models.IntegerField(verbose_name="Documento")
    telephone = models.IntegerField(verbose_name="Telefono")
    city = models.CharField(verbose_name="Ciudad", max_length=32)
    seller = models.ForeignKey(
        User,
        verbose_name="Vendedor",
        on_delete=models.CASCADE,
        default=get_default_seller,
    )

    purchase_reference = models.CharField(
        verbose_name="Referencia de compra", max_length=200, default="", blank=True, null=True
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        """
        Returns the string representation of the customer info.
        """
        return f"{self.id} | {self.name} | {self.document_number}"


PAYMENT_TYPE_CHOICES = [
    ("BONO1", "Abono 1"),
    ("BONO2", "Abono 2"),
    ("BONO3", "Abono 3"),
]


class Payment(models.Model):

    seller = models.ForeignKey(
        User, related_name="seller", verbose_name="vendedor", on_delete=models.CASCADE
    )

    client = models.ForeignKey(
        ClientInfo, related_name="payments", on_delete=models.CASCADE
    )

    payment_method = models.CharField(
        verbose_name="Metodo de pago", max_length=32, default="")

    amount = models.FloatField(verbose_name="Cantidad")
    date = models.DateTimeField(verbose_name="Fecha de Pago")
    payment_type = models.CharField(
        max_length=5, choices=PAYMENT_TYPE_CHOICES, verbose_name="Tipo de Pago"
    )

    transaction_id = models.CharField(
        verbose_name="ID de transacción", max_length=200, blank=True, null=True)
    purchase_reference = models.CharField(
        verbose_name="Referencia de compra", max_length=200, blank=True, null=True
    )

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        return f"{self.payment_method if self.payment_method else ''} - {self.transaction_id} ({self.get_payment_type_display()})"


class BankAccount(models.Model):
    """
    Model representing a bank account.

    Attributes
    ----------
    bank_name : str
        Name of the bank.
    account_name : str
        Name of the account holder.
    account_reference : int
        Reference number of the bank account.
    email : str
        Email address associated with the bank account.
    phone_number : int
        Phone number associated with the bank account.
    address_ubication : str
        Address associated with the bank account.
    """

    class Meta:
        verbose_name = "Cuenta bancaria"
        verbose_name_plural = "Cuentas bancarias"

    bank_name = models.CharField(
        verbose_name="Nombre del banco", max_length=20, choices=constants.BANK_NAMES
    )
    account_name = models.CharField(
        verbose_name="Nombre de cuenta", max_length=200)
    account_reference = models.BigIntegerField(
        verbose_name="Referencia de cuenta")
    email = models.EmailField(verbose_name="Corre electronico")
    phone_number = models.BigIntegerField(verbose_name="Numero telefonico")
    address_ubication = models.CharField(
        verbose_name="Direccion", max_length=200)

    def __str__(self):
        """
        Returns the string representation of the bank account.
        """
        return f"{self.bank_name} - {self.account_name}"


class LotteryMultimedia(models.Model):
    multimedia = CloudinaryField(
        "foto/video", resource_type="", validators=[file_validation]
    )
    lottery = models.ForeignKey("Lottery", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "multimedia"
        verbose_name_plural = "multimedias (imagenes/videos)"


BILL_TYPE_CHOICES = [
    ("TICKET_TEMPLATE", "Plantilla de boleta"),
    ("CERTIFICATE_TEMPLATE", "Plantilla de Certificado"),
]


class BillImage(models.Model):
    image = CloudinaryField(
        "foto", resource_type="", validators=[file_validation]
    )
    lottery = models.ForeignKey("Lottery", on_delete=models.CASCADE)

    image_type = models.CharField(
        max_length=20,
        choices=BILL_TYPE_CHOICES,
        verbose_name="Tipo de plantilla",
        default="TICKET_TEMPLATE"
    )

    class Meta:
        verbose_name = "Imagen de factura"
        verbose_name_plural = "Imagenes de facturas"


class Lottery(models.Model):
    """
    Model representing a lottery.

    Attributes
    ----------
    name : str
        Name of the lottery.
    multimedia : list
        List of multimedia URLs or file paths.
    description : str
        Description of the lottery.
    lottery_date : datetime
        Date and time of the lottery.
    price_per_ticket : int
        Price per ticket for the lottery.

    """

    class Meta:
        verbose_name = "Rifa"
        verbose_name_plural = "Rifas"

    name = models.CharField(verbose_name="Nombre de rifa", max_length=200)
    description = models.TextField(verbose_name="descripcion")
    lottery_date_1 = models.DateTimeField(verbose_name="Fecha de juego 1")
    lottery_date_2 = models.DateTimeField(verbose_name="Fecha de juego 2")
    lottery_date_3 = models.DateTimeField(verbose_name="Fecha de juego 3")
    lottery_date_4 = models.DateTimeField(verbose_name="Fecha de juego 4")
    price_per_ticket = models.IntegerField("precio por boleta")
    lower_series_range = models.IntegerField("Numero inicial")
    upper_series_range = models.IntegerField("Ultimo numero")

    def get_future_dates(self):
        """
        Returns a list of future dates.
        """
        now = timezone.now()  # Use timezone-aware datetime
        # Collect only future dates that are not None
        return [
            date for date in [self.lottery_date_1, self.lottery_date_2, self.lottery_date_3, self.lottery_date_4]
            if date and date >= now
        ]

    def find_nearest_date(self, dates):
        """
        Returns the nearest date from a list of dates.
        """
        now = timezone.now()  # Ensure consistency by using timezone-aware datetime
        # If there are no dates provided, return None
        if not dates:
            return None
        # Find and return the nearest date
        return min(dates, key=lambda date: abs(date - now))

    def format_date_in_spanish(self, date):
        """
        Formats the date in the 'DAY MONTH' format in Spanish.
        """
        if not date:
            return None

        # Map English month names to Spanish month names
        month_mapping = {
            'January': 'ENERO',
            'February': 'FEBRERO',
            'March': 'MARZO',
            'April': 'ABRIL',
            'May': 'MAYO',
            'June': 'JUNIO',
            'July': 'JULIO',
            'August': 'AGOSTO',
            'September': 'SEPTIEMBRE',
            'October': 'OCTUBRE',
            'November': 'NOVIEMBRE',
            'December': 'DICIEMBRE',
        }

        # Format the date to 'DAY MONTH'
        day = date.strftime('%d')
        month_english = date.strftime('%B')
        month_spanish = month_mapping.get(
            month_english, month_english).upper()  # Get the Spanish month name

        return f"{day} {month_spanish}"

    def get_nearest_formatted_date(self):
        """
        Returns the nearest lottery date from the current time, formatted as 'DAY MONTH' in Spanish.
        """
        future_dates = self.get_future_dates()
        nearest_date = self.find_nearest_date(future_dates)
        return self.format_date_in_spanish(nearest_date)

    def __str__(self):
        """
        Returns the string representation of the lottery.
        """
        return f"{self.name}"


class Ticket(models.Model):
    """
    Model representing a ticket.

    Attributes
    ----------
    number : int
        Number of the ticket.
    state : int
        State of the ticket (available, reserved, purchased).
    lottery : ForeignKey
        Reference to the related lottery.
    """

    class Meta:
        verbose_name = "Boleta"
        verbose_name_plural = "Boletas"

    number = models.IntegerField(verbose_name="numero")
    state = models.IntegerField(
        verbose_name="estado",
        choices=constants.TicketState.choices,
        default=constants.TicketState.AVAILABLE,
    )
    lottery = models.ForeignKey(
        Lottery, verbose_name="rifa", on_delete=models.CASCADE)

    def __str__(self):
        return f"Boleta {str(self.number).zfill(4)}"


class TicketReserved(models.Model):
    """
    Model representing a reserved ticket.

    Attributes
    ----------
    ticket : ForeignKey
        Reference to the related ticket.
    expiration : datetime
        Expiration date and time of the reservation.
    user : ForeignKey
        Reference to the user who reserved the ticket.
    """

    class Meta:
        verbose_name = "Boleta reservada"
        verbose_name_plural = "Boletas reservadas"

    ticket = models.ForeignKey(
        Ticket, verbose_name="Boleta", on_delete=models.CASCADE)
    expiration = models.DateTimeField(verbose_name="Fecha de expiracion")
    client = models.ForeignKey(
        ClientInfo, verbose_name="Cliente", on_delete=models.CASCADE
    )

    purchase_reference = models.CharField(
        verbose_name="Referencia de compra", max_length=200, default="", blank=True, null=True
    )

    def __str__(self):
        """
        Returns the string representation of the reserved ticket.
        """
        return f"Boleta {self.ticket.number} reservada por {self.client.name} - expira el {self.expiration.strftime('%d-%m-%Y %H:%M:%S')}"


class TicketWithPayment(models.Model):
    class Meta:
        verbose_name = "Boleta con abono"
        verbose_name_plural = "Boletas con abono"

    ticket = models.ForeignKey(
        Ticket, verbose_name="Boleta", on_delete=models.CASCADE)
    client = models.ForeignKey(
        ClientInfo, verbose_name="Cliente", on_delete=models.CASCADE
    )

    purchase_reference = models.CharField(
        verbose_name="Referencia de compra", max_length=200, default="", blank=True, null=True
    )

    def __str__(self):
        return f"Boleta {self.ticket.number}"


class TicketPendingPurchase(models.Model):
    ticket = models.ForeignKey(
        Ticket, verbose_name="Boleta", on_delete=models.CASCADE)
    expiration = models.DateTimeField(verbose_name="Fecha de expiracion")
    client = models.ForeignKey(
        ClientInfo, verbose_name="Cliente", on_delete=models.CASCADE
    )

    purchase_reference = models.CharField(
        verbose_name="Referencia de compra", max_length=200, default="", blank=True, null=True
    )

    class Meta:
        verbose_name = "Compra Pendiente"
        verbose_name_plural = "Compras Pendientes"

    def __str__(self):
        """
        Returns the string representation of the reserved ticket.
        """
        return f"Compra pendiente de boleta {self.ticket.number} para {self.client.name} - expira el {self.expiration.strftime('%d-%m-%Y %H:%M:%S')}"


class TicketPurchased(models.Model):
    """
    Model representing a purchased ticket.

    Attributes
    ----------
    ticket : ForeignKey
        Reference to the related ticket.
    user : ForeignKey
        Reference to the user who purchased the ticket.
    purchased_reference : str
        Reference for the purchase.
    """

    class Meta:
        verbose_name = "Boleta comprada"
        verbose_name_plural = "Boletas compradas"

    ticket = models.ForeignKey(
        Ticket, verbose_name="Boleta", on_delete=models.CASCADE)
    client = models.ForeignKey(
        ClientInfo, verbose_name="Cliente", on_delete=models.CASCADE
    )

    transaction_id = models.CharField(
        verbose_name="ID de transaccion", max_length=200, default="")
    purchase_reference = models.CharField(
        verbose_name="Referencia de compra", max_length=200, default="", blank=True, null=True
    )

    def __str__(self):
        """
        Returns the string representation of the purchased ticket.
        """
        return f"Boleta {self.ticket.number} comprada por {self.client.name}"


class TicketAssignment(models.Model):
    lottery = models.ForeignKey(
        Lottery, verbose_name="rifa", on_delete=models.CASCADE)

    # Fields for range assignment
    start_number = models.IntegerField(
        verbose_name="desde", null=True, blank=True)
    end_number = models.IntegerField(verbose_name="hasta", null=True, blank=True)

    # Relation for assigning individual tickets
    individual_tickets = models.ManyToManyField(
        Ticket, blank=True, verbose_name="Boletas individuales")

    assigned_to = models.ForeignKey(
        User,
        verbose_name="asignado a",
        on_delete=models.CASCADE,
    )

    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Asignar boleta"
        verbose_name_plural = "Asignación boletas"

    @classmethod
    def get_assignments_for_user(cls, user):
        return cls.objects.filter(assigned_to=user)

    def __str__(self):
        if self.start_number and self.end_number:
            return f"{self.lottery.name} - {self.start_number} to {self.end_number} assigned to {self.assigned_to.username}"
        elif self.individual_tickets.exists():
            ticket_numbers = ", ".join(
                [str(ticket.number) for ticket in self.individual_tickets.all()])
            return f"{self.lottery.name} - Tickets {ticket_numbers} assigned to {self.assigned_to.username}"
        else:
            return f"No se han asignado boletas"

    # Custom validation to ensure start_number is less than end_number
    def clean(self):
        if self.start_number and self.end_number:
            if self.start_number >= self.end_number:
                raise ValidationError(
                    "El valor de 'Desde' debe ser inferior al de 'Hasta'")

    def save(self, *args, **kwargs):
        self.clean()  # Call validation before saving
        super().save(*args, **kwargs)


class SellerBill(models.Model):
    generation_date = models.DateTimeField(verbose_name="fecha de generacion")
    seller = models.ForeignKey(
        User, verbose_name="vendedor", on_delete=models.DO_NOTHING
    )
    total_amount = models.IntegerField(verbose_name="total")

    class Meta:
        verbose_name = "Factura Vendedor"
        verbose_name_plural = "Facturas de Vendedores"


class ClientTicketPaymentBalance(models.Model):
    seller_bill = models.ForeignKey(
        SellerBill, verbose_name="factura vendedor", on_delete=models.CASCADE
    )
    client_id = models.IntegerField(verbose_name="id cliente")
    ticket_number = models.IntegerField(verbose_name="numero de boleta")
    total_amount = models.IntegerField(verbose_name="cantidad de pago total")
    last_payment_date = models.DateTimeField(verbose_name="fecha ultimo pago")

    class Meta:
        verbose_name = "Balance de pago"
        verbose_name_plural = "Balances de pago"


class PaymentContact(models.Model):
    name = models.CharField(
        verbose_name="Nombre de contacto", max_length=32, default=""
    )
    whatsapp = models.CharField(
        verbose_name="Whatsapp", max_length=32, default="")
    email = models.CharField(verbose_name="Email", max_length=32, default="")

    class Meta:
        verbose_name = "Contacto de pago"
        verbose_name_plural = "Contactos de pago"

    def __str__(self):
        return f"{ self.name }"


class Whatsapp(models.Model):
    whatsapp = models.CharField(
        verbose_name="Whatsapp", max_length=32, default="")

    class Meta:
        verbose_name = "Whatsapp"
        verbose_name_plural = "Whatsapp"

    def __str__(self):
        return f"{ self.whatsapp }"
