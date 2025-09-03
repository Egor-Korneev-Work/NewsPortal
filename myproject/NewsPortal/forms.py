from django import forms
from django.core.exceptions import ValidationError
from .models import Post, Category

class PostForm(forms.ModelForm):
   class Meta:
       model = Post
       fields = ['author', 'categories', 'title', 'content', 'rating']

   def clean(self):
       cleaned_data = super().clean()
       description = cleaned_data.get("content")
       if description is not None and len(description) < 20:
           raise ValidationError({
               "description": "Описание не может быть менее 20 символов."
           })

       return cleaned_data

       name = cleaned_data.get("title")
       if name == description:
           raise ValidationError(
               "Описание не должно быть идентичным названию."
           )

       return cleaned_data

class SubscriptionForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all())