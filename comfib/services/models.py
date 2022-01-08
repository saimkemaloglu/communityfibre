from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import NullBooleanField
from django.db.models.fields.related import ForeignKey
from django.contrib import admin

# Create your models here.

class Node(models.Model):
    node_id = models.IntegerField(primary_key=True)
    node_name = models.CharField(max_length=30)
    system_ip = models.CharField(max_length=30)

    def __str__(self):
        return self.node_name

class Port(models.Model):
    node_id = models.ForeignKey(Node, on_delete=models.CASCADE)
    port_name = models.CharField(max_length=30)

    def __str__(self):
        return self.port_name

class Service(models.Model):
    service_id = models.IntegerField(primary_key=True)
    service_id_str = models.IntegerField()
    node_id = models.ForeignKey(Node, on_delete=CASCADE)

    def __str__(self):
        return "Service: " + str(self.service_id_str)


class Sap(models.Model):
    node_id = models.ForeignKey(Node, on_delete=models.CASCADE)
    port = models.ForeignKey(Port, on_delete=models.CASCADE)
    service_id = models.ForeignKey(Service,on_delete=CASCADE)
    outer_vlan = models.IntegerField()
    inner_vlan = models.IntegerField()


class Sdp(models.Model):
    node_id = models.ForeignKey(Node, on_delete=models.CASCADE)
    sdp_id = models.IntegerField(primary_key=True)

class SdpBinding(models.Model):
    service_id = models.IntegerField(primary_key=True)
    service_id_str = models.IntegerField()
    node_id = models.ForeignKey(Service, on_delete=CASCADE)

