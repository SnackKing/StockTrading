from django import forms

class LoginForm(forms.Form):
	email = forms.EmailField(
		label = 'Email',
		max_length = 1000,
		required = True,
		widget = forms.TextInput(
	    	attrs = {'class': 'form-control mb-4 input-box-dark', 'name': 'Email'}
		)
	)   
	password = forms.CharField(
		label = 'Password',
		max_length = 1000,
		required = True,
		widget = forms.PasswordInput(
	    	attrs = {'class': 'form-control mb-4 input-box-dark', 'name': 'Password'}
		)
	)   


class SignupForm(forms.Form):
	name = forms.CharField(
    	label = 'Name',
    	max_length = 1000,
    	required = True,
    	widget = forms.TextInput(
        	attrs = {'class': 'form-control mb-4 input-box-dark', 'name': 'Name'}
    	)
	)   
	email = forms.EmailField(
		label = 'Email',
		max_length = 1000,
		required = True,
		widget = forms.TextInput(
	    	attrs = {'class': 'form-control mb-4 input-box-dark', 'name': 'Email'}
		)
	)
	code = forms.CharField(
        label = 'Join Code (Optional)',
        max_length = 10,
        required = False,
        widget = forms.TextInput(
            attrs = {'class': 'form-control mb-4 input-box-dark', 'name': 'JoinCode'}
        )
    )   
	password = forms.CharField(
		label = 'Password',
		max_length = 1000,
		required = True,
		widget = forms.PasswordInput(
	    	attrs = {'class': 'form-control mb-4 input-box-dark', 'name': 'Password'}
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

    