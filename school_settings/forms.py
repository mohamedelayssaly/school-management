from django import forms
from django.core.files.uploadedfile import UploadedFile

from accounts.models import User

from .models import SchoolProfile

MAX_LOGO_BYTES = 2 * 1024 * 1024


class SchoolProfileForm(forms.ModelForm):
    class Meta:
        model = SchoolProfile
        fields = ['name', 'slogan', 'address', 'phone', 'email', 'website', 'logo']

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if isinstance(logo, UploadedFile) and logo.size > MAX_LOGO_BYTES:
            raise forms.ValidationError('The logo must be smaller than 2 MB.')
        return logo


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'is_active']

    def __init__(self, *args, editing_self=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].help_text = 'Changes what this user can open. It does not create or remove Student or Employee records.'
        self.fields['is_active'].help_text = 'Untick to block this user from logging in.'
        if editing_self:
            del self.fields['role']
            del self.fields['is_active']