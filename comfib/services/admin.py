from django.contrib import admin
from .models import Node,Port,Service,Sap,SdpBinding,Sdp

# Register your models here.
#admin.site.register(Node,Port,Service,Sap,SdpBinding,Sdp)
""" class PortInline(admin.TabularInline):
    model = Port
    extra = 1 """

class NodeAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['node_name']}),
        ('System Ip', {'fields': ['system_ip']}),
    ]
    #inlines = [PortInline]

    list_display = ('node_name', 'system_ip')
    search_fields = ['node_name']

admin.site.register(Node,NodeAdmin)



class PortAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Port Name",{'fields':['port_name']}),
        ("Node",{'fields':['node_id']})
    ]

    list_display = ('port_name','node_id')
    search_fields = ['port_name']

admin.site.register(Port,PortAdmin)

class ServiceAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Service ID",{'fields':['service_id_str']}),
        ("Node",{'fields':['node_id']})
    ]

    list_display = ('service_id_str','node_id')
    search_fields = ['service_id_str']

admin.site.register(Service,ServiceAdmin)

class SapAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Node",{'fields':['node_id']}),
        ("Service Id",{'fields':['service_id']}),
        ("Port",{'fields':['port']}),
        ("Outer Vlan",{'fields':['outer_vlan']}),
        ("Inner Vlan",{'fields':['inner_vlan']})
    ]

    list_display = ('service_id','outer_vlan','inner_vlan')
    search_fields = ['service_id']

admin.site.register(Sap,SapAdmin)