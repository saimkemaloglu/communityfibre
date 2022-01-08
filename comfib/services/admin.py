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

admin.site.register(Port,PortAdmin)