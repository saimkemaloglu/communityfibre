from django.urls import path

from . import views

urlpatterns = [
    path('index', views.index, name='index'),
    path('creation',views.creation,name='creation'),
    path('report',views.report,name='report'),
    path('api/portData',views.get_port_data,name='port_data'),
]