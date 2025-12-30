from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Product, Category
from django.contrib.auth.forms import AuthenticationForm

from django.utils.text import slugify

class UserRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('name','email','phone_number','password1','password2')
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.name = self.cleaned_data['name']
        user.phone_number = self.cleaned_data['phone_number']
        # generate a unique username from name or email
        base = slugify(user.name) or (user.email.split('@')[0] if user.email else 'user')
        candidate = base
        i = 0
        from .models import User as UserModel
        while UserModel.objects.filter(username=candidate).exists():
            i += 1
            candidate = f"{base}{i}"
        user.username = candidate
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
