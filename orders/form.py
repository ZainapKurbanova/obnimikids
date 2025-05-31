from django import forms
from django.contrib.auth import get_user_model
from accounts.models import UserProfile

User = get_user_model()

class CheckoutForm(forms.Form):
    DELIVERY_CHOICES = [
        ('post', 'Почта России (300 ₽, 7-14 дней)'),
        ('courier', 'Курьер (500 ₽, 1-3 дня)'),
    ]

    name = forms.CharField(max_length=100, required=True, label="Имя", widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    city = forms.CharField(max_length=100, required=True, label="Город", widget=forms.TextInput(attrs={'id': 'city-input', 'autocomplete': 'off'}))
    address_detail = forms.CharField(max_length=255, required=True, label="Детальный адрес", widget=forms.TextInput(attrs={'id': 'address-detail-input', 'autocomplete': 'off'}))
    email = forms.EmailField(required=True, label="E-mail", widget=forms.EmailInput(attrs={'readonly': 'readonly'}))
    phone = forms.CharField(max_length=20, required=True, label="Телефон", widget=forms.TextInput(attrs={'placeholder': '+7 (___) ___-__-__'}))
    delivery_method = forms.ChoiceField(choices=DELIVERY_CHOICES, required=True, label="Способ доставки", widget=forms.RadioSelect)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user.is_authenticated:
            self.fields['name'].initial = user.get_full_name() or user.first_name or ''
            self.fields['email'].initial = user.email
            try:
                profile = user.profile
                if profile.phone:
                    self.fields['phone'].initial = profile.phone
                if profile.city:
                    self.fields['city'].initial = profile.city
            except UserProfile.DoesNotExist:
                pass

    def save_to_profile(self, user):
        if user.is_authenticated:
            try:
                profile, created = UserProfile.objects.get_or_create(user=user)
                phone = self.cleaned_data.get('phone')
                city = self.cleaned_data.get('city')
                if phone and not profile.phone:
                    profile.phone = phone
                if city and not profile.city:
                    profile.city = city
                profile.save()
            except Exception as e:
                print(f"Ошибка при сохранении в профиль: {e}")