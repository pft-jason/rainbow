from django.urls import path
from . import views
from .views import download_image

urlpatterns = [
    path('', views.image_list, name='image_list'),
    path('age-verification/', views.age_verification, name='age_verification'),
    path('signup/', views.signup, name='signup'), 
    path('profile/', views.profile, name='profile'), 

    path('filter/<str:officialtag>/', views.image_list, name='image_list_filtered'),
    
    path('image/<int:pk>/', views.image_detail, name='image_detail'),
    path('image/<int:pk>/edit/', views.edit_image, name='edit_image'),
    path('image/<int:pk>/delete/', views.delete_image, name='delete_image'),
    path('image/<int:pk>/favorite/', views.favorite_image, name='favorite_image'),
    path('image/<int:pk>/download/', views.download_image, name='download_image'),
    path('image/<int:pk>/fullscreen/', views.full_screen_image, name='full_screen_image'),

    path('upload/', views.upload_image, name='upload_image'), 
    path('download/<int:pk>/', views.download_image, name='download_image'),

    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('code-of-conduct/', views.code_of_conduct, name='code_of_conduct'),
    
    path('delete_all_images/', views.delete_all_images, name='delete_all_images'),
]
