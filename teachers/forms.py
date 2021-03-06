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
        label = 'Invite Code',
        max_length = 10,
        required = True,
        widget = forms.TextInput(
            attrs = {'class': 'form-control mb-4', 'name': 'JoinCode'}
        )
    )   
class NewClassForm(forms.Form):
    name = forms.CharField(
        label = 'Class Name',
        max_length = 100,
        required = True,
        widget = forms.TextInput(
            attrs = {'class': 'form-control mb-4', 'name': 'Name'}
        )
    )
    startingCash = forms.IntegerField(
        label = 'Starting Money for Students',
        required = True,
        widget = forms.NumberInput(
            attrs = {'class': 'form-control mb-4', 'name': 'StartingCash', 'min': 0}
        )
    )
    afterHoursAllowed = forms.BooleanField(
        label = "Allow After Hours Trading",
        required = False,
        widget = forms.CheckboxInput(
            attrs = {'class': 'p-3 checkbox mb-4', 'name': 'AfterHoursAllowed'}
        )

    )


class ResetPass(forms.Form):
    email = forms.EmailField(
        label = 'Email',
        max_length = 1000,
        required = True,
        widget = forms.TextInput(
            attrs = {'class': 'form-control mb-4 input-box-dark', 'name': 'Email'}
        )
    )
    