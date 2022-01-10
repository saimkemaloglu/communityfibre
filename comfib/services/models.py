from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import NullBooleanField
from django.db.models.fields.related import ForeignKey
from django.contrib import admin

# Create your models here.

class Node(models.Model):
    id = models.IntegerField(primary_key=True)
    node_name = models.CharField(max_length=30)
    system_ip = models.CharField(max_length=30)

    def __str__(self):
        return self.node_name

class Port(models.Model):
    node_id = models.ForeignKey(Node, on_delete=models.CASCADE,related_name='ports')
    port_name = models.CharField(max_length=30)

    def __str__(self):
        return "Node:"+ self.node_id.node_name +"-Port: " + str(self.port_name)

class Service(models.Model):
    id = models.IntegerField(primary_key=True)
    service_id_str = models.CharField(max_length=10)
    node_id = models.ForeignKey(Node, on_delete=CASCADE,related_name='services')

    def __str__(self):
        return "Node:"+ self.node_id.node_name +"-Service: " + str(self.service_id_str)


class Sap(models.Model):
    port = models.ForeignKey(Port, on_delete=models.CASCADE,related_name='saps')
    service_id = models.ForeignKey(Service,on_delete=CASCADE,related_name='saps')
    outer_vlan = models.IntegerField(null=True)
    inner_vlan = models.IntegerField(null=True)

    def __str__(self):
        return self.port.port_name +":" + str(self.outer_vlan)

class Sdp(models.Model):
    id = models.IntegerField(primary_key=True)
    from_node = models.ForeignKey(Node, related_name="spds_from", on_delete=models.CASCADE)
    to_node = models.ForeignKey(Node,related_name="sdps_to",on_delete=models.CASCADE)
    
    def __str__(self):
        return "from:"+ self.from_node.node_name +"-to: " + str(self.to_node.node_name)

class SdpBinding(models.Model):
    id = models.IntegerField(primary_key=True)
    sdp_id = models.ForeignKey(Sdp,related_name="bindings",on_delete=CASCADE)
    service = models.ForeignKey(Service,related_name="sdp_bindings",on_delete=CASCADE)
    vc_id = models.IntegerField()

    def __str__(self):
        return "service:"+ self.service.service_id_str +"-spoke: " + str(self.sdp_id) + ":" + str(self.vc_id)