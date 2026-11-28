from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class BootstrapFormMixin:
    """Adds Bootstrap's "form-control" class to every field's input.
    Django renders plain inputs by default, which is why they looked tiny."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class PatientRegistrationForm(BootstrapFormMixin, UserCreationForm):
    # UserCreationForm already handles password + confirmation and hashing.
    class Meta(UserCreationForm.Meta):
        model = User
        # "role" is deliberately NOT here, so nobody can pick doctor/admin
        # by editing the form in their browser.
        fields = ("username", "first_name", "last_name", "email", "phone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Replace the long always-visible rule list with one short hint.
        # The rules are still enforced: bad passwords show real errors
        # after submitting.
        self.fields["password1"].help_text = "At least 8 characters."
        self.fields["password2"].help_text = ""

    def save(self, commit=True):
        user = super().save(commit=False)
        # Always a patient, whatever the submitted data says.
        user.role = User.Role.PATIENT
        if commit:
            user.save()
        return user


class StyledAuthenticationForm(BootstrapFormMixin, AuthenticationForm):
    """Django's login form with the same Bootstrap styling."""