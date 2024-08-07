from django import forms
from .models import Image, Category, Tag, OfficialTag, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ImageUploadForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )
    official_tags = forms.ModelMultipleChoiceField(
        queryset=OfficialTag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )
    image = forms.FileField()

    class Meta:
        model = Image
        fields = ['title', 'image', 'categories', 'tags', 'description', 'official_tags']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['categories'].queryset = Category.objects.all()
        self.fields['tags'].queryset = Tag.objects.all()
        self._handle_user_specific_fields()

    def _handle_user_specific_fields(self):
        if not (self.user and self.user.is_staff):
            self.fields.pop('official_tags')

    def save(self, commit=True):
        
        image = super().save(commit=False)
        image.uploaded_by = self.user
        image.moderated = self.user.is_staff if self.user else False
        if commit:
            image.save()
            self.save_m2m()
            if 'official_tags' in self.cleaned_data:
                image.official_tag.set(self.cleaned_data['official_tags'])
        return image

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']  # Assuming 'text' is the field for comment content

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget = forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3,
            'placeholder': 'Enter your comment here...'
        })

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
