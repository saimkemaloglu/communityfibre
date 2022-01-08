import json
import textfsm
from srosparser import ServiceSlicing
import requests
import pandas as pd



def groupByPortId(sapList):
  portMap = {}
  portDict = {"name":[],"count":[]}
  for sap in sapList:
    if ":" in sap:
      port = sap.split(":")[0]
      if port in portMap:
        portMap[port] = portMap[port] + 1
      else:
        portMap[port] = 1
    """ else:
      port = sap
      if port in portMap:
        portMap[port] = portMap[port] + 1
      else:
        portMap[port] = 1 """

  for port in portMap:
    portDict["name"].append(port)
    portDict["count"].append(portMap[port])

  if portDict:
    return portDict

      



if __name__ == '__main__':  
  with open('configs/config-rel-10.cfg') as f:
    con = f.read()
    # print con[:1000]
    conf = ServiceSlicing(con)
    #print (dir(conf))
    print (conf.host_name())
    print (conf.system_ip_address())
    ## print(conf.sap_list_return())
    ##svc_sect = conf._svc_sect_slice()
    sapList = conf.sap_list_return()
    grouped = groupByPortId(sapList)
    ##sapsDetail = {}
    dfOfPorts = pd.DataFrame(grouped).sort_values(by='count',ascending=False)
    print(dfOfPorts.to_string())
    #print(json.dumps(grouped)) 

  """  ##Grafana api related parts
  server = "https://saimkemaloglu.grafana.net"
  # Example 1: Get default Home dashboard:
  url = server + "/api/dashboards/home"
  # To get the dashboard by uid
  # url = server + "/api/dashboards/uid/" + uid
  headers = {"Authorization":"Bearer eyJrIjoiZ1QwQnI0YWUxMkc1QnpLcjBkbHA3ektKMk9RTWxld1IiLCJuIjoic2FpbSIsImlkIjoxfQ=="}
  r = requests.get(url = url, headers = headers, verify=False)
  print(r.json()) """

      ##Grafana api related parts end

        ##sapDetail = conf.sap_parms(sapList,svc_sect)
        ##print (json.dumps(sapsDetail, indent=4))
        # print conf.system_ip()
        # svc_sect = conf._svc_sect_slice()
        # print svc_sect[:100]
        # c_list = conf.customer_list(svc_sect)
        # print c_list
        # conf = PolicyParms(con)
        # pol_sec = conf._policy_sect_slice()
        # pol_l = conf.policy_list(pol_sec)
        # print pol_l[:3]
        # pre_l = conf.prefix_list(pol_sec)
        # # print pre_l[:3]
        # com_d = conf.community_dict(pol_sec)
        # # print com_d.keys()
        # pre_d = conf.prefix_dict(pre_l[:1], pol_sec)
        # pol_d = conf.policy_dict(pol_l[:1], pol_sec)
        # print pol_d[pol_l[0]]

