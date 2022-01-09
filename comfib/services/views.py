import os
from django.db import models
from django.db.models.query import RawQuerySet
from django.shortcuts import redirect, render
from django.http import HttpResponse,JsonResponse
from services.srosparser import ServiceSlicing
import pandas as pd
from .models import Node,Port,Sap,Service,Sdp,SdpBinding
from django.core import serializers

# Create your views here.
def index(request):
    return render(request, 'services/index.html')

def creation(request):
    return render(request,'services/servicecreation.html')

def createEline(request):
  if request.method == 'POST':
    nodeA = list(Node.objects.filter(node_id=request.POST['NodeA']).values_list('system_ip',flat=True))[0]
    nodeB = list(Node.objects.filter(node_id=request.POST['NodeB']).values_list('system_ip',flat=True))[0]
    portA = list(Port.objects.filter(node_id=int(request.POST['NodeA']),id=int(request.POST['PortA'])).values_list('port_name',flat=True))[0]
    portB = list(Port.objects.filter(node_id=int(request.POST['NodeB']),id=int(request.POST['PortB'])).values_list('port_name',flat=True))[0]
    print ("node a:"+nodeA+" nodeB:"+ nodeB + "a: "+portA + "b: "+portB)
    data = {
      'node_a': nodeA,
      'node_b': nodeB,
      'port_a': portA,
      'port_b': portB,
      'vlana':request.POST['VlanA'],
      'vlanb':request.POST['VlanB'],
      'serviceId':request.POST['ServiceId'],
      'sdpa':request.POST['sdpAB'],
      'sdpb':request.POST['sdpBA'],
      'vcid':request.POST['vcId'],
    }
    return render(request,'services/createEline.html',data)
  else:
    return redirect('services:creation')

def report(request):
    return render(request,'services/report.html')

def get_port_data(request,*args):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)
    filepath = dir_path + '/configs/'
    data = getSapPerPort(filepath)
    return JsonResponse(data)

def get_node_ports(request,node_id):
  ports = Port.objects.filter(node_id=node_id).values()
  return JsonResponse(list(ports),safe=False)

def get_node_sdps(request,node_id):
  sdps = Sdp.objects.filter(from_node_id=node_id).values()
  return JsonResponse(list(sdps),safe=False)

def get_nodes(request):
  #nodes = Node.objects.all()
  #data = serializers.serialize('json', nodes)
  return JsonResponse(list(Node.objects.all().values()), safe=False)


def groupByPortId(sapList):
  portDict = {}
  for sap in sapList:
    if ":" in sap:
      port = sap.split(":")[0]
      if port in portDict:
        portDict[port] = portDict[port] + 1
      else:
        portDict[port] = 1
    """ else:
      port = sap
      if port in portMap:
        portMap[port] = portMap[port] + 1
      else:
        portMap[port] = 1 """
  portTemp = sorted(portDict, key=portDict.get, reverse=True)
  returnDict = {}
  if len(portTemp) > 10:
    for i in range(0,10):
      returnDict[portTemp[i]] = portDict[portTemp[i]]
  else:
    for i in range(0,len(portTemp)):
      returnDict[portTemp[i]] = portDict[portTemp[i]]
    
  if returnDict:
    return returnDict

def getSapPerPort(folder):
  wholeThing = {}
  listDir = os.listdir(folder)
  dir_path = os.path.dirname(os.path.realpath(__file__))
  for file in listDir:
    with open(dir_path+"/configs/"+file) as f:
        con = f.read()
        conf = ServiceSlicing(con)
        sapList = conf.sap_list_return()
        nodeSap = {'name':conf.host_name(),'systemIp':conf.system_ip_address(),'totalSapCount':len(sapList)}
        grouped = groupByPortId(sapList)
        mergedPortAndNode = {'port':grouped,'node':nodeSap}
        ##sapsDetail = {}
    wholeThing[file]= mergedPortAndNode
  print(wholeThing)  
  return wholeThing