from django import forms
from .models import FarmerRegistration


class FarmerRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = FarmerRegistration
        fields = [
            "full_name",
            "mobile",
            "email",
            "land_record",
            "state",
            "district",
            "taluka",
            "village",
        ]
