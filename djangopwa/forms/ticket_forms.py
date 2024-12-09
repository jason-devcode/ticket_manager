from djangopwa.models import TicketAssignment, Ticket
from djangopwa.models import TicketAssignment
from django import forms
from django.db.models import Min, Max

from djangopwa import models
from djangopwa import constants
from types import NoneType


class TicketReserveForm(forms.Form):
    name = forms.CharField(label="Nombre:", max_length=32)
    lastname = forms.CharField(label="Apellido:", max_length=32)
    document_number = forms.CharField(label="CC:", max_length=32)
    whatsapp = forms.IntegerField(label="Whatsapp:")
    city = forms.CharField(label="Ciudad:", max_length=64)
    seller_id = forms.CharField(label="id vendedor:", max_length=64)
    ticket_number_to_reserve = forms.IntegerField(
        label="Numero de rifa a separar:", min_value=0, max_value=9999
    )

    def clean_whatsapp(self):
        whatsapp = self.cleaned_data.get("whatsapp")
        if len(str(whatsapp)) < constants.MAX_WHATSAPP_DIGITS:
            raise forms.ValidationError(
                f"El número de WhatsApp debe tener al menos {constants.MAX_WHATSAPP_DIGITS} dígitos."
            )
        return whatsapp

    def clean_ticket_number_to_reserve(self):
        ticket_number_to_reserve = self.cleaned_data.get(
            "ticket_number_to_reserve")

        ticket = models.Ticket.objects.filter(
            number=ticket_number_to_reserve, state=constants.TicketState.AVAILABLE
        )

        if not ticket.exists():
            raise forms.ValidationError(
                "El número de rifa no está disponible.")

        return ticket_number_to_reserve


class TicketAssignmentForm(forms.ModelForm):
    class Meta:
        model = TicketAssignment
        fields = ["lottery", "individual_tickets",
                  "assigned_to", "start_number", "end_number"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        lottery = models.Lottery.objects.latest("id")
        self.fields["lottery"].initial = lottery.id
        self.fields["lottery"].disabled = True  # Disable editing

        tickets = lottery.ticket_set.exclude(
            ticketassignment__isnull=False
        ).exclude(
            number__range=(
                models.TicketAssignment.objects.filter(lottery=lottery)
                .aggregate(min_number=Min('start_number'), max_number=Max('end_number'))
                .values()
            )
        )
        
        if 'instance' in kwargs:
            instance = kwargs['instance']
            if instance is not None and not isinstance(instance, NoneType) and instance.pk:
                self.instance = instance
                assigned_tickets = instance.individual_tickets.all()
                self.fields['individual_tickets'].queryset = assigned_tickets | tickets
                self.fields['individual_tickets'].initial = assigned_tickets
        else:
            self.fields['individual_tickets'].queryset = tickets

    def clean(self):
        cleaned_data = super().clean()
        assigned_to = cleaned_data.get("assigned_to")
        start_number = cleaned_data.get("start_number")
        end_number = cleaned_data.get("end_number")
        lottery = cleaned_data.get("lottery")

        if assigned_to and start_number is not None and end_number is not None and lottery:
            if TicketAssignment.objects.filter(
                lottery=lottery,
                start_number__lte=end_number,
                end_number__gte=start_number,
            ).exclude(assigned_to=assigned_to).exists():
                raise forms.ValidationError(
                    f"Tickets in the specified range for lottery {lottery} have already been assigned to another user."
                )

        return cleaned_data
