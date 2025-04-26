# likeSys/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('documents/<uuid:doc_id>/', views.document_detail, name='document_detail'),
    path('documents/<uuid:doc_id>/submit_rating/', views.submit_rating, name='submit_rating'),
]