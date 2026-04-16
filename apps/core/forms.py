from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    kvkk_consent = forms.BooleanField(
        required=True,
        label=_("Aydınlatma Metni'ni okudum ve kabul ediyorum."),
    )

    class Meta:
        model = ContactMessage
        fields = ("name", "email", "phone", "subject", "message", "kvkk_consent")
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": _("Ad Soyad"),
                    "autocomplete": "name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-input",
                    "placeholder": _("E-posta"),
                    "autocomplete": "email",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": _("Telefon (opsiyonel)"),
                    "autocomplete": "tel",
                }
            ),
            "subject": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": _("Konu (opsiyonel)"),
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "placeholder": _("Mesajınız"),
                    "rows": 5,
                }
            ),
        }
