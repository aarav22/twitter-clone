from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserForm(UserCreationForm):
    email = forms.EmailField()
    

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        del self.fields['password2']
        del self.fields['password1']
        User.set_unusable_password(self)

    class Meta:
        model = User
        fields = ['username', 'email']
        exclude = ['password1', 'password2']
        
    # def clean_password2(self):
    #     password1 = self.cleaned_data.get("password1")
    #     password2 = self.cleaned_data.get("password2")
    #     if password1 and password2 and password1 != password2:
    #         raise forms.ValidationError(
    #             self.error_messages['password_mismatch'],
    #             code='password_mismatch',
    #         )
    #     return password2 
