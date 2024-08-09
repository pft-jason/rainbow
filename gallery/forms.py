from django import forms
from .models import Image, Category, Tag, OfficialTag, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image as PilImage
from io import BytesIO
import uuid
from dirtydeedz.s3_client import client
from .settings import get_env_variable


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

        if self.cleaned_data.get('image'):
            full_image = self.cleaned_data['image']
            random_name = f'{uuid.uuid4()}.jpeg'
            full_image_name = f'full.{random_name}'
            gallery_image_name = f'gallery.{random_name}'

            # Create gallery image
            img = PilImage.open(full_image)
            output_size = (512, 512)
            img.thumbnail(output_size)
            buffer = BytesIO()
            img.save(buffer, format='JPEG')
            buffer.seek(0)

            # Upload full image to Spaces
            full_image.seek(0)  # Reset file pointer to the beginning
            client.put_object(Bucket=get_env_variable('DO_BUCKET_NAME'), Key=full_image_name, Body=full_image.read(), ACL='public-read')
            image.full_image_url = f'{get_env_variable("DO_SPACES_ENDPOINT")}/{get_env_variable("DO_BUCKET_NAME")}/{full_image_name}'

            # Upload gallery image to Spaces
            client.put_object(Bucket=get_env_variable('DO_BUCKET_NAME'), Key=gallery_image_name, Body=buffer.read(), ACL='public-read')
            image.gallery_image_url = f'{get_env_variable("DO_SPACES_ENDPOINT")}/{get_env_variable("DO_BUCKET_NAME")}/{gallery_image_name}'

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
