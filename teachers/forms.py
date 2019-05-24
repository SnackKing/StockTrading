from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(
        label = 'Teacher Email',
        max_length = 1000,
        required = True,
        widget = forms.TextInput(
            attrs = {'class': 'form-control mb-4', 'name': 'Email'}
        )
    )   
    password = forms.CharField(
        label = 'Password',
        max_length = 1000,
        required = True,
        widget = forms.PasswordInput(
            attrs = {'class': 'form-control mb-4', 'name': 'Password'}
        )
    )   


class SignupForm(forms.Form):
    name = forms.CharField(
        label = 'Name',
        max_length = 1000,
        required = True,
        widget = forms.TextInput(
            attrs = {'class': 'form-control mb-4', 'name': 'Name'}
        )
    )   
    email = forms.EmailField(
        label = 'Teacher Email',
        max_length = 1000,
        required = True,
        widget = forms.TextInput(
            attrs = {'class': 'form-control mb-4', 'name': 'Email'}
        )
    )   
    password = forms.CharField(
        label = 'Password',
        max_length = 1000,
        required = True,
        widget = forms.PasswordInput(
            attrs = {'class': 'form-control mb-4', 'name': 'Password'}
        )
    )
    code = forms.CharField(
        label = 'Join Code',
        max_length = 10,
        required = True,
        widget = forms.TextInput(
            attrs = {'class': 'form-control mb-4', 'name': 'JoinCode'}
        )


    )   
    