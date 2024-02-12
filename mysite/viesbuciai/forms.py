from django import forms
from .models import Profile, Hotel, Order, AdminDetails
from django.contrib.auth.models import User
from django import forms
from datetime import timedelta, date
import re


class ProfileForm(forms.ModelForm):
    """
    Profilio formos su jų specifiniais laukais (vardas, pavardė, adresas, miestas, šalis)
    Pridėtas datos widget'as, kad gimimo datą butų galima rinktis iš meniu.
    """

    birth_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))

    class Meta:
        model = Profile
        fields = ['name', 'lastname', 'birth_date', 'address', 'city', 'country']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['birth_date'].label = "Gimimo data"


class RegistrationForm(forms.ModelForm):
    """
    Registracijos forma (el. paštas, slaptažodžiai (pirmas ir antras)
    El. pašto tikrinimas, ar jau nėra sukurtas (unikalumo tikrinimas)
    Regex panaudojimas siekiant nustatyti slaptažodžio kriterijus.
    """
    email = forms.EmailField(required=True, widget=forms.EmailInput())
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match.")

        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$", cd['password2']):
            raise forms.ValidationError('Password must contain at least 8 characters, one uppercase letter,'
                                        ' one lowercase letter, and one number')
        return cd['password2']


class HotelSelectForm(forms.Form):
    """
    Hotelio pasirinkimo forma naudojama iš hotels.html)
    """
    hotel = forms.ModelChoiceField(queryset=Hotel.objects.all())


class OrderForm(forms.ModelForm):
    """
    Užsakymo forma (rezervacijos)
    Naudojami datos laukai (widget'ai) dėl datos posirinkimo
    """

    r_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), initial=date.today)
    i_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), initial=date.today()+timedelta(days=1))

    class Meta:
        model = Order
        fields = ['r_date', 'i_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['r_date'].label = "Įsiregistravimo data"
        self.fields['i_date'].label = "Išsiregistravimo data"


class EditOrderForm(forms.ModelForm):
    """
    Užsakymo redagavimo forma su lauku - 'status'
    Teisės tik admin useriui.
    """
    class Meta:
        model = Order
        fields = ['status']


class EditAdminDetailsForm(forms.ModelForm):
    """
    Admin detalių priskyrimas jau egzistuojančiam užsakymui.
    Prieiga tik admin useriui.
    Panaudoti laukeliai (kambario numeris, aukštas ir ramybės valandų laukelis)
    """
    class Meta:
        model = AdminDetails
        fields = ['room_id', 'aukstas', 'ramybes_valandos']


class HotelForm(forms.ModelForm):
    """
    Naujo kuriamo hotelio forma.
    Panaudota kambario pavadinimas, tipas, žvaigždės (reitingas), kaina, adresas,
    aprašymas, kiekis (žmonių max), prieinamumas (kiek viešbučių galima rezervuoti)
    Sukūrimo prieiga tik admin useriui.
    """
    class Meta:
        model = Hotel
        fields = ['name', 'type', 'stars', 'price', 'address', 'description', 'quantity', 'availability']
