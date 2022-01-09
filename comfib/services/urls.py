from django.urls import path
from . import views

app_name = "services"
urlpatterns = [
    path('', views.index, name='index'),
    path('creation',views.creation,name='creation'),
    path('createEline',views.createEline,name='createEline'),
    path('report',views.report,name='report'),
    path('api/portData',views.get_port_data,name='port_data'),
    path('api/nodes',views.get_nodes,name='get_nodes'),
    path('api/<int:node_id>/ports/',views.get_node_ports,name='get_node_ports'),
    path('api/<int:node_id>/sdps/',views.get_node_sdps,name='get_node_sdps'),
]