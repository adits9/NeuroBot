from django.urls import path
from .views import UploadEEGAPIView

urlpatterns = [
    path('upload_eeg/', UploadEEGAPIView.as_view(), name='upload_eeg'),
]
