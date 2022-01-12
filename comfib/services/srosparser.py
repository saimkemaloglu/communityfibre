import re
import json


class ServiceSlicing(object):
    def __init__(self, config):
        self.config = config
        self.hostname = None
        self.system_ip = None
        self.sap_list = None

    def host_name(self):
        try:
            self.hostname = re.search('[ ]{4}system[\r|\n]+[ ]{8}name "(.*)"',self.config).group(1)
        except Exception as f:
            print(f)
            return False
        return self.hostname

    def system_ip_address(self):
        try:
            self.system_ip = re.search('"system"[\r\n]+[ ]{12}address (\d+.\d+.\d+.\d+)/\d+',self.config).group(1)
        except Exception as f:
            print(f)
            return False
        return self.system_ip

    def sap_list_return(self):
        self.sap_list = re.findall('\s+sap (\S+)', self.config)
        return self.sap_list


