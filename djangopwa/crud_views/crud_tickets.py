from django.views import generic
from django.urls import path, reverse
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone


import random

from djangopwa import models
from djangopwa import constants
from djangopwa.forms import ticket_forms


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


class TicketView(generic.DetailView):
    model = models.Ticket
    template_name = "tickets/tickets.html"
    context_object_name = "ticket"

    def get_object(self):
        lottery_id = self.kwargs.get("lottery_id")
        ticket_number = self.kwargs.get("pk")  # pk is used for ticket number here
        return get_object_or_404(
            models.Ticket, lottery_id=lottery_id, number=ticket_number
        )

    def get_context_data(self, **kwargs):
        """
        Get and modify the context data for the view.
        """
        context = super().get_context_data(**kwargs)

        ticket = context.get("ticket")

        if ticket.state == constants.TicketState.PURCHASED:
            ticket_purchased = models.TicketPurchased.objects.get(ticket=ticket)
            client = ticket_purchased.client

        if ticket.state == constants.TicketState.RESERVED:
            ticket_reserved = models.TicketReserved.objects.get(ticket=ticket)
            client = ticket_reserved.client

        if client:
            payment_count = models.Payment.objects.filter(client=client).count()
            client_context = {
                "name_and_lastname": mask_after_third_character(client.name)
                + " "
                + mask_after_third_character(client.lastname),
                "document_number": mask_except_last_three_characters(
                    str(client.document_number)
                ),
                "payment_count": payment_count,
            }

            context["client"] = client_context

        return context


class TicketLuckyRouletteView(generic.TemplateView):
    template_name = "tickets/tickets_lucky_roulette.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lottery = models.Lottery.objects.latest("id")
        context["lottery_id"] = lottery.id
        return context


class RandomAvailableTicketAPIView(generic.View):
    def get(self, request, *args, **kwargs):
        """
        Get a random available ticket from the database for the specified lottery.

        Returns:
            JsonResponse: A JSON response containing the details of the selected ticket.
        """
        lottery_id = kwargs.get("lottery_id")
        # Filter available tickets for the specified lottery
        available_tickets = models.Ticket.objects.filter(state=1, lottery_id=lottery_id)
        available_tickets_count = available_tickets.count()

        if available_tickets_count == 0:
            # No available tickets found for the specified lottery
            return JsonResponse({"error": "No available tickets for this lottery"})

        # Choose a random index within the range of available tickets
        random_index = random.randint(0, available_tickets_count - 1)

        # Retrieve the randomly chosen ticket
        random_ticket = available_tickets[random_index]

        # Prepare the response data
        response_data = {
            "ticket_number": random_ticket.number,
        }

        return JsonResponse(response_data)


class TicketReserveView(generic.FormView):
    """
    View for reserving a ticket.

    Attributes
    ----------
    template_name : str
        The template to render.
    form_class : forms.Form
        The form class to use for the reservation.

    Methods
    -------
    form_valid(form)
        Handles the form submission if it is valid.
    """

    template_name = "tickets/tickets_reserve_ticket.html"
    form_class = ticket_forms.TicketReserveForm

    def get_initial(self):
        """
        Get the initial data for the form.

        This method is used to pre-fill the form fields with initial data
        if provided in the URL parameters.

        Returns
        -------
        dict
            A dictionary containing the initial form data.
        """
        initial = super().get_initial()
        ticket_number = self.request.GET.get("ticket_number")
        if ticket_number:
            initial["ticket_number_to_reserve"] = ticket_number
        initial["seller_id"] = 1
        return initial

    def form_valid(self, form):
        """
        Process the valid form submission.

        This method retrieves or creates a user based on the submitted form data,
        retrieves the specified ticket for the lottery and marks it as reserved,
        creates a TicketReserved entry with an expiration time, and redirects to
        the ticket detail page.

        Parameters
        ----------
        form : forms.Form
            The submitted form instance.

        Returns
        -------
        HttpResponseRedirect
            A redirect to the ticket detail page.
        """
        lottery_id = self.kwargs.get("lottery_id")
        ticket_number = form.cleaned_data.get("ticket_number_to_reserve")
        name = form.cleaned_data.get("name")
        document_number = form.cleaned_data.get("document_number")
        lastname = form.cleaned_data.get("lastname")
        whatsapp = form.cleaned_data.get("whatsapp")
        city = form.cleaned_data.get("city")

        # Retrieve the ticket and update its state to reserved
        ticket = get_object_or_404(
            models.Ticket,
            number=ticket_number,
            lottery_id=lottery_id,
            state=constants.TicketState.AVAILABLE,
        )

        lottery = get_object_or_404(
            models.Lottery,
            id=lottery_id,
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
        )
        client.save()

        ticket.state = constants.TicketState.RESERVED
        ticket.save()

        # Create a TicketReserved entry
        expiration = timezone.now() + timezone.timedelta(
            days=constants.MAX_TIME_DAYS_RESERVATION_TICKET
        )

        models.TicketReserved.objects.create(
            ticket=ticket,
            expiration=expiration,
            user=client,
        ).save()

        # Redirect to a success page or another view
        return HttpResponseRedirect(
            reverse(
                "ticket_detail",
                kwargs={"lottery_id": ticket.lottery_id, "pk": ticket.number},
            )
        )


urlpatterns = [
    path(
        "lottery/<int:lottery_id>/ticket/<int:pk>",
        TicketView.as_view(),
        name="ticket_detail",
    ),
    path(
        "lottery/lucky_roulette",
        TicketLuckyRouletteView.as_view(),
        name="ticket_lucky_roulette",
    ),
    path(
        "lottery/<int:lottery_id>/reserve_ticket",
        TicketReserveView.as_view(),
        name="tickets_reserve_ticket_form",
    ),
    path(
        "api/lottery/<int:lottery_id>/random_available_ticket/",
        RandomAvailableTicketAPIView.as_view(),
        name="random_available_ticket_api",
    ),
]
