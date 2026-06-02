from django import forms

class LoginForm(forms.Form):
    login = forms.CharField(min_length=3, max_length=20)
    password = forms.CharField(widget=forms.PasswordInput())

class SearchForm(forms.Form):
    search = forms.CharField(min_length=0, max_length=20)
