from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class': 'form-control'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password',
        'class': 'form-control'
    }))
    class Meta:
        model = Account

        fields = [
            'first_name',
            'last_name',
            'phone_num',
            'email',
            'password',
        ]
    
    def __init__(self,*args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder']= 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder']= 'Enter Last Name'
        self.fields['email'].widget.attrs['placeholder']= 'Enter Email Address'
        self.fields['phone_num'].widget.attrs['placeholder']= 'Enter the Phone number'
        for field in self.fields:
            self.fields[field].widget.attrs['class']= 'form-control'
    

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        have_uper = 0

        if confirm_password == password:
            if len(password) >= 8:
                for i in password:
                    if i.isupper():
                        have_uper += 1
                if have_uper >= 1:
                    pass
                else:
                    raise forms.ValidationError('Password need at least 1 upper case character.')
            else:
                raise forms.ValidationError('Password need at least 8 characters')
        else:
            raise forms.ValidationError('Password not match')