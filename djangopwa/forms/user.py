from django import forms

from djangopwa import models
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class BaseUserForm(forms.ModelForm):
    required_fields = [
        "first_name",
        "last_name",
        "email",
        "document_number",
        "whatsapp",
    ]

    def clean(self):
        cleaned_data = super().clean()
        for field in self.required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, "Este campo es obligatorio.")
        return cleaned_data


class CustomUserChangeForm(UserChangeForm, BaseUserForm):
    class Meta:
        model = models.User
        fields = "__all__"


class CustomUserCreationForm(UserCreationForm, BaseUserForm):
    class Meta:
        model = models.User
        fields = "__all__"

class PaymentContactForm(forms.ModelForm):
    name = forms.CharField(label="Nombre de contacto:", max_length=32)
    whatsapp = forms.CharField(label="Whatsapp(opcional):", max_length=32, required=False)
    email = forms.CharField(label="Correo electronico(opcional):", max_length=32, required=False)