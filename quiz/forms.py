from django import forms


class EmailGateForm(forms.Form):
    email = forms.EmailField(
        label="Your email",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "you@example.com",
            "autofocus": True,
        }),
    )
