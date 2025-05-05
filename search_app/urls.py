from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("reddit_search/", views.reddit_search, name="reddit_search"),
    path('save_results/', views.save_results, name='save_results'),
]