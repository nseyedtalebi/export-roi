from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'get_roi_patches/(\d+)', views.get_roi_patches,name='get_roi_patches')
]