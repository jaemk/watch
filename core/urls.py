from django.conf.urls import url
from core import views

urlpatterns = [
    url(r'login/$', views.Login.as_view(), name='login'),
    url(r'logout/$', views.logout, name='logout'),
    url(r'home/$', views.Home.as_view(), name='home'),
    url(r'cam/toggle/$', views.ToggleCamera.as_view(), name='toggle_cam'),
    url(r'cam/status/$', views.CameraStatus.as_view(), name='cam_status'),
    url(r'upload/$', views.camera_upload, name='upload'),

    # secured uploaded media files
    url(r'media/.*', views.SecureMedia.as_view(), name='secure_media'),

    url(r'', views.into_home, name='into_home'),
]
