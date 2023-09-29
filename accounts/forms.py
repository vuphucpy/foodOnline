from django import forms

from .models import User


# User form
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username',
                  'email']

    # clean data
    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # compare password and confirm_password
        if password != confirm_password:
            # non field error
            raise forms.ValidationError(
                'Password does not match!'
            )
