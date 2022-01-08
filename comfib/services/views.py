import os
from django.db import models
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from services.srosparser import ServiceSlicing
import pandas as pd
from .models import Node,Port,Sap,Service,Sdp,SdpBinding

# Create your views here.
def index(request):
    return render(request, 'services/index.html')

def creation(request):
    return render(request,'services/servicecreation.html')

def report(request):
    return render(request,'services/report.html')

def get_port_data(request,*args):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)
    filepath = dir_path + '/configs/'
    data = getSapPerPort(filepath)
    return JsonResponse(data)



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
        #print (conf.host_name())
        #print (conf.system_ip_address())
        ## print(conf.sap_list_return())
        ##svc_sect = conf._svc_sect_slice()
        sapList = conf.sap_list_return()
        nodeSap = {'name':conf.host_name(),'systemIp':conf.system_ip_address(),'totalSapCount':len(sapList)}
        grouped = groupByPortId(sapList)
        mergedPortAndNode = {'port':grouped,'node':nodeSap}
        ##sapsDetail = {}
    wholeThing[file]= mergedPortAndNode
  print(wholeThing)  
  return wholeThing