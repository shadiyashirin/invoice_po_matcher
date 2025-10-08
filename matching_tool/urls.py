from django.urls import path
from . import views

#app_name = 'matching_tool'

'''urlpatterns = [
    path('', views.upload_documents, name='upload'),
    path('results/<int:match_id>/', views.match_results, name='match_results'),
    path('documents/', views.document_list, name='document_list'),
]'''

'''urlpatterns = [
    path('', views.upload_documents, name='upload_documents'),
    path('results/', views.match_results, name='match_results'),
]'''

urlpatterns = [
    # This line maps the homepage URL ('') to the 'upload_and_match_view'
    # function in views.py.
    path('', views.upload_and_match_view, name='upload'),
]
