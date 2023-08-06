from django import forms
from django.forms import ModelForm
from .models import Comments


class UploadPostForm(forms.Form):
    file = forms.FileField()


class CommentForm(ModelForm):
    class Meta:
        model = Comments
        fields = ["comment"]
