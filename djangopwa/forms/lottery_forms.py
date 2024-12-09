from django import forms

from djangopwa import models

# Formulary classes to customize input widgets


class LotteryCreateForm(forms.ModelForm):
    class Meta:
        model = models.Lottery
        fields = "__all__"


class LotteryPurchaseDataForm(forms.Form):
    name = forms.CharField(label="Nombre:", max_length=32)
    lastname = forms.CharField(label="Apellido:", max_length=32)
    document_number = forms.IntegerField(label="CC:")
    whatsapp = forms.IntegerField(label="Whatsapp:")
    city = forms.CharField(label="Ciudad:", max_length=32)
    seller_id = forms.CharField(label="ID Vendedor ( Opcional ):", max_length=32, required=False)
    amount_to_pay = forms.CharField(label="Cantidad a pagar:", max_length=32)
 