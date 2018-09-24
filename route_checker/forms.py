from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import BusUser, Buses

class BusForm(forms.ModelForm):
    bus = forms.CharField(label='Bus')

    class Meta:
        model = Buses
        fields = ['bus',]

class UserAdminCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = BusUser
        fields = ('email',)

    def cleanPassWord(self):
        # check that the two password entries match
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class UserAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = BusUser
        fields = ('email', 'password', 'active', 'admin')

    def cleanPassword(self):
        return self.initial['password']

class LoginForm(forms.Form):
    username = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput)
