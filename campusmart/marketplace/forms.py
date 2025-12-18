from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Product, Category
from django.contrib.auth.forms import AuthenticationForm

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username','first_name','last_name','email','phone_number','password1','password2')
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')


class ProductUploadForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title','description','category','cost','image']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control','placeholder':'Enter product title'}),
            'description': forms.Textarea(attrs={'class':'form-control','rows':4,'placeholder':'Describe your product'}),
            'category': forms.Select(attrs={'class':'form-control'}),
            'cost': forms.NumberInput(attrs={'class':'form-control','placeholder':'Enter price in rupees'}),
            'image': forms.FileInput(attrs={'class':'form-control','accept':'image/*'})
        }
