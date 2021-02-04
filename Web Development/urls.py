from django.urls import path
from . import views

app_name = 'search'
urlpatterns = [
    path('browse/<slug:slug_text>', views.categories_results, name='categories_results'),
    path('browse', views.categories, name='categories'),
    path('blog/<slug:slug_text>', views.blog_detail, name='blog_detail'),
    path('blogs', views.blogs, name='blogs'),
    path('', views.index, name='index'),
    path('search', views.search, name='search'),
    path('privacy-policy', views.privacy_policy, name="privacy")
]
