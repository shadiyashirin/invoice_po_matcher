from django.urls import path
from . import views

#app_name = 'matching_tool'

urlpatterns = [
    # This line maps the homepage URL ('') to the 'upload_and_match_view'
    # function in views.py.
    path('', views.upload_and_match_view, name='upload'),
]
