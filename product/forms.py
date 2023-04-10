from django import forms
from .models import Feedback


class FeedbackForm(forms.ModelForm):

    """Форма для добавления отзыва"""

    class Meta:
        model = Feedback
        fields = ['rating', 'description', 'image']


class UploadProductFileJsonForm(forms.Form):

    """Форма добавление товаров, продавцов и т.п через файл JSON"""

    file_json = forms.FileField(required=False, label='Загрузить файл формата JSON')
