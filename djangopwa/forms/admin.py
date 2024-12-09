from django import forms

from djangopwa import models
from djangopwa import constants


class ClientInfoAdminForm(forms.ModelForm):
    class Meta:
        model = models.ClientInfo
        fields = "__all__"


class PaymentForm(forms.ModelForm):
    class Meta:
        model = models.Payment
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        # Verifica si al menos dos campos están completos.
        filled_fields = [
            field for field in cleaned_data if cleaned_data[field]]
        if len(filled_fields) < 2:
            self.cleaned_data = {}  # Vacía cleaned_data para evitar el guardado
        return cleaned_data


class TicketReservedForm(forms.ModelForm):
    # Campos de ClientInfo
    client_name = forms.CharField(
        max_length=32, required=True, label="Nombres")
    client_lastname = forms.CharField(
        max_length=32, required=True, label="Apellidos")
    client_whatsapp = forms.CharField(
        max_length=15, required=True, label="Whatsapp")
    client_document_number = forms.CharField(
        max_length=50, required=True, label="Número de Documento")
    client_telephone = forms.CharField(
        max_length=15, required=True, label="Teléfono")
    client_city = forms.CharField(max_length=32, required=True, label="Ciudad")
    lottery_to_buy = forms.ModelChoiceField(
        queryset=models.Lottery.objects.all(), required=False, label="Rifa a comprar")
    ticket = forms.ModelChoiceField(
        queryset=models.Ticket.objects.none(), required=False, label="Número de rifa")
    seller = forms.ModelChoiceField(queryset=models.User.objects.filter(
        is_active=True), required=True, label="Vendedor")

    class Meta:
        model = models.TicketReserved
        fields = ['lottery_to_buy', 'ticket', 'seller', 'expiration', 'client_name', 'client_lastname',
                  'client_whatsapp', 'client_document_number', 'client_telephone',
                  'client_city']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get('instance')

        if instance and instance.client:
            # Pre-populate fields with related ClientInfo data
            self.fields['client_name'].initial = instance.client.name
            self.fields['client_lastname'].initial = instance.client.lastname
            self.fields['client_whatsapp'].initial = instance.client.whatsapp
            self.fields['client_document_number'].initial = instance.client.document_number
            self.fields['client_telephone'].initial = instance.client.telephone
            self.fields['client_city'].initial = instance.client.city

    def save(self, commit=True):
        # Save client info from form data
        ticket = self.cleaned_data.get('ticket')
        ticket.state = constants.TicketState.RESERVED

        client_info = models.ClientInfo(
            name=self.cleaned_data['client_name'],
            lastname=self.cleaned_data['client_lastname'],
            whatsapp=self.cleaned_data['client_whatsapp'],
            document_number=self.cleaned_data['client_document_number'],
            telephone=self.cleaned_data['client_telephone'],
            city=self.cleaned_data['client_city'],
            lottery_to_buy=self.cleaned_data.get('lottery_to_buy'),
            ticket_number=self.cleaned_data.get('ticket'),
            seller=self.cleaned_data['seller'],
            purchase_reference=self.cleaned_data.get('purchase_reference', '')
        )

        # Save the ClientInfo instance before assigning it to the TicketReserved
        client_info.save()

        pending_purchase = models.TicketPendingPurchase(
            ticket=ticket, client=client_info, expiration=self.cleaned_data['expiration'], purchase_reference=self.cleaned_data.get('purchase_reference', ''))

        # Save the TicketReserved instance
        ticket_reserved = super().save(commit=False)
        ticket_reserved.client = client_info  # Now assign the saved ClientInfo instance

        pending_purchase.save()
        ticket_reserved.save()
        # Save the ticket state update
        ticket.save()

        return ticket_reserved
