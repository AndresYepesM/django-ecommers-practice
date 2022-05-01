from django import forms
from .models import Account, UserProfile

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


class UserForm(forms.ModelForm):
    class Meta:
        model = Account

        fields = [
            'first_name',
            'last_name',
            'phone_num'
        ]
    def __init__(self,*args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['first_name']
        self.fields['last_name']
        self.fields['phone_num']
        for field in self.fields:
            self.fields[field].widget.attrs['class']= 'form-control'

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile

        fields =[
            'address_line1',
            'address_line2',
            'profile_picture',
            'city',
            'state',
            'country'
        ]

    def __init__(self,*args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['address_line1']
        self.fields['address_line2']
        self.fields['profile_picture']
        self.fields['city']
        self.fields['state']
        self.fields['country']
        for field in self.fields:
            self.fields[field].widget.attrs['class']= 'form-control'