from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.urls import reverse_lazy, path, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db.models import Count

from djangopwa import models
from djangopwa import constants
from djangopwa.forms import lottery_forms
from lottery.wompi import wompi


class LotteryView(generic.TemplateView):
    """
    View to visualize lottery information.

    Attributes
    ----------
    model : Model
        The model that this view will display, in this case, the Lottery model.
    template_name : str
        The template to render for this view.
    context_object_name : str
        The context variable name for the object being viewed.
    """

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        """
        Add multimedia URLs to the context.

        Parameters
        ----------
        kwargs : dict
            Additional context variables.

        Returns
        -------
        dict
            Context data for rendering the template.
        """
        context = super().get_context_data(**kwargs)
        lottery = models.Lottery.objects.latest("id")

        multimedia_urls = [
            {
                "url": media.multimedia.url,
                "is_video": media.multimedia.url.endswith(".mp4"),
            }
            for media in lottery.lotterymultimedia_set.all()
        ]
        context["multimedia_urls"] = multimedia_urls

        context["nearest_date"] = lottery.get_nearest_formatted_date()

        lottery_media = [
            {
                "url": media.multimedia.url,
                "is_video": media.multimedia.url.endswith(".mp4"),
            }
            for media in lottery.lotterymultimedia_set.all()
        ]
        formatted_price = f"{lottery.price_per_ticket:,}".replace(",", ".")
        context["formatted_price"] = formatted_price

        context["tickets"] = lottery.ticket_set.all()
        context["lottery"] = lottery
        context["lottery_id"] = lottery.id
        context["lottery_media"] = lottery_media
        return context


class LotteryViewSelectTicketOptions(generic.TemplateView):
    template_name = "lottery/lottery_select_ticket_options.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lottery = models.Lottery.objects.latest("id")

        formatted_price = f"{lottery.price_per_ticket:,}".replace(",", ".")

        context["formatted_price"] = formatted_price
        context["lottery"] = lottery

        return context


def create_ticket_purchases(purchase_data):
    lottery_id = purchase_data.get("lottery_id")

    ticket_numbers = purchase_data.get("ticket_numbers")
    purchase_reference = purchase_data.get("purchase_reference")

    name = purchase_data.get("name")
    city = purchase_data.get("city")
    document_number = purchase_data.get("document_number")
    lastname = purchase_data.get("lastname")
    whatsapp = purchase_data.get("whatsapp")
    seller_id = purchase_data.get("seller_id")
    
    seller = None
    
    if seller_id:
        try:
            seller_id = int(seller_id)  # Convert to integer
            seller = models.User.objects.get(id=seller_id)
            print(seller)
        except ValueError:
            print("Seller ID must be a valid number.")
        except models.User.DoesNotExist:
            print(f"Seller with ID {seller_id} does not exist.")
    else:
        print("Seller ID is not provided.")
        
    lottery = get_object_or_404(
        models.Lottery,
        id=lottery_id,
    )

    # Retrieve the ticket and update its state to reserved
    for ticket_number in ticket_numbers:
        ticket = get_object_or_404(
            models.Ticket,
            number=ticket_number,
            lottery_id=lottery_id,
            state=constants.TicketState.AVAILABLE,
        )
        # Retrieve or create user
        client = models.ClientInfo.objects.create(
            name=name,
            lastname=lastname,
            whatsapp=whatsapp,
            telephone=whatsapp,
            document_number=document_number,
            city=city,
            lottery_to_buy=lottery,
            ticket_number=ticket,
            purchase_reference=purchase_reference,
        )
        
        if seller:
            client.seller = seller

        ticket.state = constants.TicketState.RESERVED

        # Create a TicketReserved entry
        expiration = timezone.now() + timezone.timedelta(
            days=constants.MAX_TIME_DAYS_RESERVATION_TICKET
        )

        ticket_reserved = models.TicketReserved.objects.create(
            ticket=ticket,
            expiration=expiration,
            client=client,
            purchase_reference=purchase_reference,
        )

        ticket_pending_purchase = models.TicketPendingPurchase.objects.create(
            ticket=ticket,
            expiration=expiration,
            client=client,
            purchase_reference=purchase_reference,
        )

        ticket.save()
        client.save()
        ticket_reserved.save()
        ticket_pending_purchase.save()


class LotteryPurchaseDataFormView(generic.edit.FormView):
    """
    View to handle lottery purchase data form submission.
    """

    form_class = lottery_forms.LotteryPurchaseDataForm
    template_name = "lottery/lottery_purchase_data_form.html"

    def check_tickets_state(self, lottery_id, ticket_numbers):
        try:
            lottery = models.Lottery.objects.filter(id=lottery_id).first()

            for ticket_number in ticket_numbers:
                ticket = models.Ticket.objects.filter(
                    lottery=lottery, number=ticket_number
                ).first()
                if ticket.state != constants.TicketState.AVAILABLE:
                    return False
        except Exception as e:
            return False
        return True

    def get_ticket_numbers(self):
        ticket_numbers_str = self.request.GET.get("ticket_numbers", "")
        ticket_numbers = []

        if ticket_numbers_str:
            ticket_numbers = [
                int(ticket_number) for ticket_number in ticket_numbers_str.split(",")
            ]
        return ticket_numbers

    def get_context_data(self, **kwargs):
        """
        Add query parameters to the context data.

        Parameters
        ----------
        kwargs : dict
            Additional context data.

        Returns
        -------
        dict
            The context data dictionary with the query parameters added.
        """
        context = super().get_context_data(**kwargs)

        lottery_id = self.kwargs["pk"]
        ticket_numbers = self.get_ticket_numbers()

        isTicketsAvailable = (
            self.check_tickets_state(
                lottery_id=lottery_id, ticket_numbers=ticket_numbers
            )
            and ticket_numbers.__len__() >= 1
        )

        lottery = models.Lottery.objects.get(id=lottery_id)

        CENTS_PER_PESO = 100

        amount_to_pay = (
            lottery.price_per_ticket * ticket_numbers.__len__() * CENTS_PER_PESO
        )

        purchase_reference = wompi.generate_purchase_reference()
        integrity_signature = wompi.generate_hash_integrity_signature(
            purchase_reference, amount_to_pay
        )

        wompi_redirect_url = (
            f"{wompi.base_redirect_url}/lottery/{lottery_id}/payment_gateway"
        )

        # Add query parameters to the context
        context["ticket_numbers"] = ticket_numbers
        context["all_tickets_available"] = isTicketsAvailable
        context["WOMPI_PUBLIC_KEY"] = wompi.credentials.public_key
        context["AMOUNT_TO_PAY_IN_CENTS"] = amount_to_pay
        context["PURCHASE_REFERENCE"] = purchase_reference
        context["INTEGRITY_SIGNATURE"] = integrity_signature
        context["WOMPI_REDIRECT_URL"] = wompi_redirect_url

        return context

    def form_valid(self, form):
        lottery_id = self.kwargs.get("pk")
        ticket_numbers = self.get_ticket_numbers()

        name = form.cleaned_data.get("name")
        city = form.cleaned_data.get("city")
        document_number = form.cleaned_data.get("document_number")
        lastname = form.cleaned_data.get("lastname")
        seller_id = form.cleaned_data.get("seller_id")
        whatsapp = form.cleaned_data.get("whatsapp")

        amount_to_pay = form.cleaned_data.get("amount_to_pay")

        # Remove periods and the $ symbol if they exist
        amount_to_pay = amount_to_pay.replace('.', '').replace('$', '')

        # Cast the cleaned string to an integer
        amount_to_pay = int(amount_to_pay)

        purchase_reference = wompi.generate_purchase_reference()

        lottery_purchase_data = {
            "lottery_id": lottery_id,
            "ticket_numbers": ticket_numbers,
            "name": name,
            "city": city,
            "document_number": document_number,
            "lastname": lastname,
            "whatsapp": whatsapp,
            "purchase_reference": purchase_reference,
            "amount_to_pay": amount_to_pay,
            "seller_id": seller_id
        }

        self.request.session["lottery_purchase_data"] = lottery_purchase_data

        create_ticket_purchases(lottery_purchase_data)

        return redirect("lottery_payment_gateway", pk=self.kwargs["pk"])


class LotteryPaymentGatewayView(generic.DetailView):

    model = models.Lottery
    template_name = "payment/payment_gateway.html"
    context_object_name = "lottery"

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            lottery_id = self.kwargs["pk"]

            ticket_numbers = self.request.session["lottery_purchase_data"][
                "ticket_numbers"
            ]

            purchase_reference = self.request.session["lottery_purchase_data"][
                "purchase_reference"
            ]

            amount_to_pay = self.request.session["lottery_purchase_data"][
                "amount_to_pay"
            ]

            CENTS_PER_PESO = 100

            amount_to_pay = amount_to_pay * CENTS_PER_PESO

            integrity_signature = wompi.generate_hash_integrity_signature(
                purchase_reference, amount_to_pay
            )

            wompi_redirect_url = (
                f"{wompi.base_redirect_url}/lottery/pending-purchase"
            )

            # Add query parameters to the context
            context["WOMPI_PUBLIC_KEY"] = wompi.credentials.public_key
            context["AMOUNT_TO_PAY_IN_CENTS"] = amount_to_pay
            context["PURCHASE_REFERENCE"] = purchase_reference
            context["INTEGRITY_SIGNATURE"] = integrity_signature
            context["WOMPI_REDIRECT_URL"] = wompi_redirect_url
            context["status"] = True
        except Exception as e:
            context["status"] = False

        return context


class LotteryFailureTransaction(generic.TemplateView):
    template_name = "payment/failure_transaction.html"


class LotteryPendingPurchase(generic.TemplateView):
    template_name = "payment/pending_purchase.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment_contacts = models.PaymentContact.objects.all()
        context["payment_contacts"] = payment_contacts
        return context


class LotterySelectTicketView(generic.TemplateView):
    """
    View to select ticket number view.
    """
    template_name = "lottery/lottery_select_ticket.html"

    def get_context_data(self, **kwargs):
        """
        Get and modify the context data for the view.
        """
        context = super().get_context_data(**kwargs)

        lottery = models.Lottery.objects.latest("id")

        context["lottery"] = lottery

        # Add tickets data related to lottery object
        context["tickets"] = lottery.ticket_set.all()
        return context


urlpatterns = [
    path("", LotteryView.as_view(), name="lottery_detail"),
    path("ticket_select_options", LotteryViewSelectTicketOptions.as_view(),
         name="ticket_select_options"),
    path(
        "lottery/<int:pk>/purchase_data",
        LotteryPurchaseDataFormView.as_view(),
        name="lottery_purchase_data_form",
    ),
    path(
        "lottery/select_ticket/",
        LotterySelectTicketView.as_view(),
        name="lottery_select_ticket",
    ),
    path(
        "lottery/<int:pk>/payment_gateway",
        LotteryPaymentGatewayView.as_view(),
        name="lottery_payment_gateway",
    ),
    path(
        "lottery/failure-transaction",
        LotteryFailureTransaction.as_view(),
        name="lottery_failure_transaction",
    ),
    path(
        "lottery/pending-purchase",
        LotteryPendingPurchase.as_view(),
        name="lottery_pending_purchase",
    ),
]
