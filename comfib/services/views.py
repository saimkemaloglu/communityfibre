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
    filepath = 'services/configs/config-rel-10.cfg'
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
  for i in range(0,10):
    returnDict[portTemp[i]] = portDict[portTemp[i]]
    
  if returnDict:
    return returnDict

def getSapPerPort(file):
    with open(file) as f:
        con = f.read()
        # print con[:1000]
        conf = ServiceSlicing(con)
        #print (dir(conf))
        
        print (conf.host_name())
        print (conf.system_ip_address())
        ## print(conf.sap_list_return())
        ##svc_sect = conf._svc_sect_slice()
        sapList = conf.sap_list_return()
        nodeSap = {'name':conf.host_name(),'systemIp':conf.system_ip_address(),'totalSapCount':len(sapList)}
        grouped = groupByPortId(sapList)
        mergedPortAndNode = {'port':grouped,'node':nodeSap}
        ##sapsDetail = {}
        return mergedPortAndNode