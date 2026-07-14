from django import forms
from .models import market_databaze,User

class add_market(forms.ModelForm):
    class Meta:
        model = market_databaze
        fields = '__all__'
        exclude = ['author']

class register(forms.ModelForm):
    class Meta:
        model = User
        fields = ['phone', 'avatar','username','password']

    def save(self, commit=True):
        customuser = super().save(commit=False)

        if 'password' in self.cleaned_data:
            customuser.set_password(self.cleaned_data['password'])

        if commit:
            customuser.save()

        return customuser