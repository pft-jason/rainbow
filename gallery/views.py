from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Image, Category, Tag
from django.core.paginator import Paginator
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import ImageUploadForm, CommentForm
from django.db.models import Q, Count
from .forms import CustomUserCreationForm

from django.db.models import Count, Q, IntegerField, Value
from django.db.models.functions import Coalesce

def image_list(request):
    filter_by = request.GET.get('filter', 'all')
    sort_by = request.GET.get('sort', 'new')
    selected_tags = request.GET.getlist('tags')
    
    # Convert tag names to IDs
    selected_tag_ids = Tag.objects.filter(name__in=selected_tags).values_list('id', flat=True)
    
    images = Image.objects.filter(moderated=True)
    
    if filter_by == 'favorites':
        images = images.filter(favorites__id=request.user.id)
    elif filter_by == 'uploads':
        images = images.filter(uploaded_by=request.user)
    
    images = images.annotate(matching_tags=Count('tags', filter=Q(tags__in=selected_tag_ids)))

    if sort_by == 'new':
        images = images.order_by('-matching_tags', '-uploaded_at')
    elif sort_by == 'favorite':
        images = images.annotate(favorite_count=Count('favorites')).order_by('-matching_tags', '-favorite_count')
    elif sort_by == 'downloads':
        images = images.order_by('-matching_tags', '-downloads')
    elif sort_by == 'popular':
        images = images.annotate(comment_count=Count('comments')).order_by('-matching_tags', '-comment_count')
    
    paginator = Paginator(images, 20)  # Show 20 images per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    all_tags = Tag.objects.annotate(num_images=Count('image')).filter(num_images__gt=0)
    
    return render(request, 'gallery/image_list.html', {
        'page_obj': page_obj,
        'filter_by': filter_by,
        'sort_by': sort_by,
        'selected_tags': selected_tags,
        'all_tags': all_tags,
    })

def image_detail(request, pk):
    image = get_object_or_404(Image, pk=pk)
    is_favorited = False
    
    if request.user.is_authenticated:
        is_favorited = image.favorites.filter(id=request.user.id).exists()
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.image = image
            comment.user = request.user
            comment.save()
            # return redirect('image_detail', pk=image.pk)
            return redirect(f'{request.path}?new_comment=true')
    else:
        comment_form = CommentForm()

    comments = image.comments.all()

    context = {
        'image': image,
        'is_favorited': is_favorited,
        'comment_form': comment_form,
        'comments': comments,
        'downloads': image.downloads, 
    }
    return render(request, 'gallery/image_detail.html', context)

@login_required
def favorite_image(request, pk):
    image = get_object_or_404(Image, pk=pk)
    if image.favorites.filter(id=request.user.id).exists():
        image.favorites.remove(request.user)
    else:
        image.favorites.add(request.user)
    return redirect('image_detail', pk=image.pk)

def age_verification(request):
    if request.method == 'POST':
        # Set session variable when the user verifies their age
        request.session['age_verified'] = True
        return redirect('image_list')  # Redirect to the main page after verification
    return render(request, 'gallery/age_verification.html')

@login_required
def profile(request):
    user = request.user
    pending_uploaded_images = Image.objects.filter(uploaded_by=user, moderated=False)
    approved_uploaded_images = Image.objects.filter(uploaded_by=user, moderated=True)

    paginator = Paginator(approved_uploaded_images, 6)  # Show 10 images per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'gallery/profile.html', {
        'pending_uploaded_images': pending_uploaded_images,
        'page_obj': page_obj
    })



def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('image_list')  # Redirect to the main page after signing up
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('image_list')
    else:
        form = ImageUploadForm(user=request.user)
    return render(request, 'gallery/upload_image.html', {'form': form})

def full_screen_image(request, pk):
    image = get_object_or_404(Image, pk=pk)
    return render(request, 'gallery/full_screen_image.html', {'image': image})

@login_required
def edit_image(request, pk):
    image = get_object_or_404(Image, pk=pk, uploaded_by=request.user)
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES, instance=image, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('image_detail', pk=image.pk)
    else:
        form = ImageUploadForm(instance=image, user=request.user)
    return render(request, 'gallery/edit_image.html', {'form': form, 'image': image})

@login_required
def delete_image(request, pk):
    image = get_object_or_404(Image, pk=pk, uploaded_by=request.user)
    if request.method == 'POST':
        image.delete()
        return redirect('profile')
    return render(request, 'gallery/delete_image.html', {'image': image})

@login_required
def download_image(request, pk):
    image = get_object_or_404(Image, pk=pk)
    image.downloads += 1
    image.save()
    response = HttpResponse(image.image, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{image.image.name}"'

    # Redirect to the same page after download
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('image_detail', pk=pk)

    
    # Redirect to the same page after download
    return redirect(request.META.get('HTTP_REFERER', 'image_detail', pk=pk))

def disclaimer(request):
    return render(request, 'gallery/disclaimer.html')

def code_of_conduct(request):
    return render(request, 'gallery/code_of_conduct.html')