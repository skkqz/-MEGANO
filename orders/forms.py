from django import forms
from .models import Order, DELIVERY_CHOICES, TYPE_CHOICES


class OrderUserCreateForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=50)
    number = forms.IntegerField(min_value=100000, max_value=89999999999, widget=forms.TextInput())
    password1 = forms.CharField(widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-group'}),
        }


class OrderDeliveryCreateForm(forms.Form):
    delivery = forms.ChoiceField(choices=DELIVERY_CHOICES)
    city = forms.CharField(max_length=100)
    address = forms.CharField(max_length=250)


class OrderPaymentCreateForm(forms.Form):
    payment = forms.ChoiceField(choices=TYPE_CHOICES)


class OrderCardForm(forms.Form):
    card_number = forms.CharField(min_length=8, max_length=9, required=True, label='Номер карты',)


class OrderCommentForm(forms.Form):
    comment = forms.CharField(max_length=500, widget=forms.Textarea, required=True, label='Комментарий к заказу',)
