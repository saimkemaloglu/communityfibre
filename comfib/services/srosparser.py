import re
import json


class ServiceSlicing(object):
    def __init__(self, config):
        self.config = config
        self.hostname = None
        self.system_ip = None
        self.sap_list = None
        self.sdp_using_list = None

    def host_name(self):
        try:
            self.hostname = re.search('[ ]{4}system[\r|\n]+[ ]{8}name "(.*)"',
                                                        self.config).group(1)
        except Exception as f:
            print(f)
            return False
        return self.hostname

    def system_ip_address(self):
        try:
            self.sys_ip = re.search('"system"[\r\n]+[ ]{12}address (\d+.\d+.\d+.\d+)/\d+',
                                                                 self.config).group(1)
        except Exception as f:
            print(f)
            return False
        return self.sys_ip

    def sap_list_return(self):
        self.sap_list = re.findall('\s+sap (\S+)', self.config)
        return self.sap_list

    def sdp_using_return(self):
        self.sdp_using = re.findall('-sdp (\S+)', self.config)
        return self.sdp_using

    def _search_func(self, search_for, search_in):
        try:
            ser_object = re.search('{}'.format(search_for), search_in).group(1)
        except Exception:
            ser_object = False
        return ser_object

    def _svc_sect_slice(self):
        '''finds service section in the conf file'''
        try:
            section_start = self.config.index('echo "Service Configuration"')
        except Exception as f:
            print ('Error: {}'.format(f))
        else:
            section_end = '\n    exit'
            ser_section = self.config[section_start:]
            try:
                service_section = ser_section[:ser_section.index(section_end)]
            except Exception as f:
                print ('Error: {}'.format(f))
            else:
                return service_section

    def customer_list_return(self, service_section):
        '''returns all customer IDs configured on the node'''
        customer_list = re.findall('[\r\n]+[ ]{8}customer (\d+)', service_section)
        return customer_list

    def sdp_list_return(self, service_section):
        '''returns all SDP IDs configured on the node'''
        sdp_list = re.findall('[\r\n]+[ ]{8}sdp (\d+).*create', service_section)
        return sdp_list

    def _find_section(self, spaces, search_element, search_section, search_id=None):
        '''finds section for particular id and returns it
            section can be customer, sdp.. section_id: 1,2,3...'''
        if search_id:
            search_expression = '[\r\n]+([ ]{{{}}}{}[ ]{}([ ]|[\r\n]+))'.format(spaces, search_element, search_id)
        else:
            search_expression = '[\r\n]+([ ]{{{}}}{})([ ]|[\r\n]+)'.format(spaces, search_element)
        search_regex = self._search_func(search_expression, search_section)
        if search_regex:
            section_begin_index = search_section.index(search_regex)
            section_begin = search_section[section_begin_index:]
            section_end_re = re.search('[\r\n]+[ ]{{{}}}exit'.format(spaces), search_section).group(0)
            section_end_index = section_begin.index(section_end_re)
            section = section_begin[:section_end_index]
            return section

    def customer_parms(self, customer_list, service_section):
        '''returns dictionary of all customer id-s and related description'''
        cust_dict = {}
        for cust_id in customer_list:
            cust_sect = self._find_section(8, 'customer', service_section, cust_id)
            cust_desc = self._search_func('description "(.*)"', cust_sect)
            cust_dict.update({cust_id: cust_desc})
        if cust_dict:
            return cust_dict

    def sdp_parms(self, sdp_list, service_section):
        '''returns dictionary of all SDP-s and related parameters'''
        sdp_dict = {}
        for sdp_id in sdp_list:
            sdp_sect = self._find_section(8, 'sdp', service_section, sdp_id)
            sdp_desc = self._search_func('description "(.*)"', sdp_sect)
            sdp_far_end = self._search_func('far-end (\d+\.\d+\.\d+\.\d+)', sdp_sect)
            sdp_ldp = self._search_func('(ldp)', sdp_sect)
            sdp_lsp = self._search_func('lsp "(.*)"', sdp_sect)
            sdp_path_mtu = self._search_func('path-mtu (\d+)', sdp_sect)
            sdp_up = self._search_func('[ ]{12}(no shutdown)', sdp_sect)
            sdp_binding_port = self._search_func('[ ]{16}port (.*)', sdp_sect)
            sdp_pw_ports = re.findall('pw-port (\d+ vc-id \d+) create', sdp_sect)
            sdp_bgp = self._search_func('[ ]{12}bgp-tunnel', sdp_sect)
            sdp_dict.update({sdp_id: {
                'description': sdp_desc,
                'far-end': sdp_far_end,
                'ldp': sdp_ldp,
                'lsp': sdp_lsp,
                'path-mtu': sdp_path_mtu,
                'sdp-up': sdp_up,
                'binding-port': sdp_binding_port,
                'pw-ports': sdp_pw_ports,
                'bgp_tunnel': sdp_bgp
                }
            })
        if sdp_dict:
            return sdp_dict

    def svc_type(self, svc_id, service_section):
        space = '[\r\n]+[ ]{8}'
        expression = '(\w+)[ ]{}'.format(svc_id)
        svc_type = self._search_func('{}{}'.format(space, expression), service_section)
        return svc_type

    def sap_parms(self, sap_list, svc_sect):
        '''returns dictionary of SAP parameters'''
        sap_dict = {}
        for sap in sap_list:
            if sap:
                if ':' in sap:
                    sap_vlan = sap.split(':')[1]
                    sap_port = sap.split(':')[0]
                else:
                    sap_vlan = False
                    sap_port = sap
                sap_sect = self._find_section(16, 'sap', svc_sect, sap)
                sap_desc = self._search_func('[\r\n]+[ ]{20}description "(.*)"', sap_sect)
                ingress_sec = self._find_section(20, 'ingress', sap_sect)
                egress_sec = self._find_section(20, 'egress', sap_sect)
                qos_ingress = self._search_func('[\r\n]+[ ]{24}qos (\d+)', ingress_sec)
                sched_ingress = self._search_func('[\r\n]+[ ]{24}scheduler-policy "(.*)"', ingress_sec)
                filter_ingress = self._search_func('[\r\n]+[ ]{24}filter (.*)', ingress_sec)
                qos_egress = self._search_func('[\r\n]+[ ]{24}qos (\d+)', egress_sec)
                sched_egress = self._search_func('[\r\n]+[ ]{24}scheduler-policy "(.*)"', egress_sec)
                filter_egress = self._search_func('[\r\n]+[ ]{24}filter (.*)', egress_sec)
                sap_state = self._search_func('[\r\n]+[ ]{20}(no shutdown)', sap_sect)
                sap_dict.update({sap: {
                    'id': sap,
                    'port': sap_port,
                    'vlan': sap_vlan,
                    'description': sap_desc,
                    'qos_ingress': qos_ingress,
                    'sched_ingress': sched_ingress,
                    'filter_ingress': filter_ingress,
                    'qos_egress': qos_egress,
                    'sched_egress': sched_egress,
                    'filter_egress': filter_egress,
                    'state': sap_state
                }})
        if sap_dict:
            return sap_dict

    def sdp_using_list(self, service_sect):
        '''returns all vpls IDs configured on the node'''
        sdp_list = re.findall('[\r\n]+[ ]{12}((?:(?:mesh)|(?:spoke))-sdp.*) create', service_sect)
        return sdp_list

    def sdp_using_parms(self, sdp_list, svc_sect):
        '''returns dictionary of SAP parameters'''
        sdp_dict = {}
        for sdp in sdp_list:
            s_id = self._search_func('-sdp (\d+:\d+)', sdp)
            sdp_id = s_id.split(':')[0]
            sdp_vc_id = s_id.split(':')[1]
            sdp_type = self._search_func('(\S+)-sdp \d+:\d+', sdp)
            sdp_vc_type = self._search_func('\d+:\d+ vc-type (\S+)', sdp)
            sdp_r_l_t = self._search_func('\d+:\d+.*(root-leaf-tag)', sdp)
            sdp_leaf = self._search_func('\d+:\d+.*(leaf-ac)', sdp)
            sdp_shg = self._search_func('-sdp[ ]\d+:\d+.*split-horizon-group "(.*)"', sdp)
            sdp_end = self._search_func('-sdp[ ]\d+:\d+.*endpoint "(.*)"', sdp)
            sdp_options = self._search_func('-sdp \d+:\d+[ ](.*)', sdp)
            sdp_sect = self._find_section(12, sdp, svc_sect)
            sdp_desc = self._search_func('[\r\n]+[ ]{16}description "(.*)"', sdp_sect)
            sdp_state = self._search_func('[\r\n]+[ ]{16}(no shutdown)', sdp_sect)
            sdp_dict.update({s_id: {
                'id': sdp_id,
                'vc-id': sdp_vc_id,
                'type': sdp_type,
                'vc-type': sdp_vc_type,
                'root-l-t': sdp_r_l_t,
                'leaf': sdp_leaf,
                'shg': sdp_shg,
                'endpoint': sdp_end,
                'options': sdp_options,
                'description': sdp_desc,
                'state': sdp_state
            }})
        if sdp_dict:
            return sdp_dict

    def static_routes(self, spaces, config_section):
        '''returns all static routes configured on the config_section'''
        space = '[\r\n]+[ ]{{{}}}'.format(spaces)
        content = 'static-route \d+\.\d+\.\d+\.\d+/\d+.*'
        static_routes = re.findall('{}({})'.format(space, content), config_section)
        return static_routes

    def bgp_sect(self, spaces, config_section):
        bgp_sect = self._find_section(spaces, 'bgp', config_section)
        return bgp_sect

    def bgp_parms(self, spaces, bgp_sect):
        '''returns all bgp paramters'''
        space = '[\r\n]+[ ]{{{}}}'.format(spaces + 4)
        bgp_vpn_im = self._search_func('{}vpn-apply-import'.format(space), bgp_sect)
        bgp_vpn_ex = self._search_func('{}vpn-apply-export'.format(space), bgp_sect)
        return {'vpn-apply-import': bgp_vpn_im,
                'vpn-apply-export': bgp_vpn_ex}

    def bgp_groups(self, bgp_sect):
        bgp_group_list = re.findall('group "(.*)"', bgp_sect)
        return bgp_group_list

    def bgp_group_parms(self, spaces, bgp_group_list, bgp_sect):
        '''returns dictionary of all BGP groups and related parameters'''
        bgp_gr_dict = {}
        for b_group in bgp_group_list:
            space = '[\r\n]+[ ]{{{}}}'.format(spaces+4)
            group_sect = self.bgp_group_sect(spaces, bgp_sect, b_group)
            # g_name = b_group
            g_family = self._search_func('{}family (.*)'.format(space), group_sect)
            g_type = self._search_func('{}type (.*)'.format(space), group_sect)
            g_export = self._search_func('{}export (.*)'.format(space), group_sect)
            g_neighbors = re.findall('{}neighbor (\d+.\d+.\d+.\d+)'.format(space), group_sect)
            bgp_gr_dict.update({b_group: {
                # 'name': g_name,
                'family': g_family,
                'type': g_type,
                'export': g_export,
                'neighbors': g_neighbors
            }})
        if bgp_gr_dict:
            return bgp_gr_dict

    def bgp_group_sect(self, spaces, bgp_sect, b_group):
        group_sect = self._find_section(spaces, 'group', bgp_sect, '"{}"'.format(b_group))
        return group_sect

    def bgp_neighbor_parms(self, spaces, bgp_neighbor_list, group_sect):
        '''returns dictionary of all BGP neighbors and related parameters'''
        neighbor_dict = {}
        for neighbor in bgp_neighbor_list:
            space = '[\r\n]+[ ]{{{}}}'.format(spaces+4)
            neighbor_sect = self._find_section(spaces, 'neighbor', group_sect, '{}'.format(neighbor))
            neighbor_family = self._search_func('{}family (.*)'.format(space), neighbor_sect)
            neighbor_type = self._search_func('{}type (.*)'.format(space), neighbor_sect)
            neighbor_export = self._search_func('{}export (.*)'.format(space), neighbor_sect)
            neighbor_peer = self._search_func('{}peer-as (.*)'.format(space), neighbor_sect)
            neighbor_dict.update({neighbor: {
                'family': neighbor_family,
                'type': neighbor_type,
                'export': neighbor_export,
                'peer-as': neighbor_peer
            }})
        if neighbor_dict:
            return neighbor_dict


class VprnParms(ServiceSlicing):
    def __init__(self, service_section):
        self.service_section = service_section

    def vprn_list(self, service_section):
        '''returns all VPRN IDs configured on the node'''
        vprn_ids = re.findall('[\r\n]+[ ]{8}vprn (\d+) customer', service_section)
        vprn_set = set(vprn_ids)
        return list(vprn_set)

    def vprn_section(self, vprn_id, service_section):
        v_find = re.findall('[\r\n]+[ ]{{8}}vprn {} customer'.format(vprn_id), service_section)
        if len(v_find) == 2:
            vprn_section = service_section.split('vprn {} customer'.format(vprn_id), 1)[1]
            vprn_sect = self._find_section(8, 'vprn', vprn_section, vprn_id)
            return vprn_sect

    def vprn_parms(self, vprn_id, vprn_sect):
        '''returns dictionary of all VPRN-s and related parameters'''
        vprn_dict = {}
        # for vprn_id in vprn_list:
        vprn_cust = self._search_func('vprn \d+ customer (\d+)', vprn_sect)
        vprn_desc = self._search_func('[\r\n]+[ ]{12}description "(.*)"', vprn_sect)
        vprn_name = self._search_func('[\r\n]+[ ]{12}service-name "(.*)"', vprn_sect)
        vprn_import = self._search_func('[\r\n]+[ ]{12}vrf-import (.*)', vprn_sect)
        vprn_export = self._search_func('[\r\n]+[ ]{12}vrf-export (.*)', vprn_sect)
        vprn_as = self._search_func('[\r\n]+[ ]{12}autonomous-system (\d+)', vprn_sect)
        vprn_rd = self._search_func('[\r\n]+[ ]{12}route-distinguisher (\S+:\S+)', vprn_sect)
        vprn_target = self._search_func('[\r\n]+[ ]{12}vrf-target (.*)', vprn_sect)
        vprn_autobind = self._search_func('[\r\n]+[ ]{12}auto-bind (.*)', vprn_sect)
        vprn_res_filter = self._search_func('[\r\n]+[ ]{12}(resolution-filter)', vprn_sect)
        vprn_res_gre = self._search_func('[\r\n]+[ ]{20}(gre)', vprn_sect)
        vprn_res_ldp = self._search_func('[\r\n]+[ ]{20}(ldp)', vprn_sect)
        vprn_res_rsvp = self._search_func('[\r\n]+[ ]{20}(rsvp)', vprn_sect)
        if vprn_import:
            vrf_im = re.findall('"(.*?)"', vprn_import)
        else:
            vrf_im = vprn_import
        if vprn_export:
            vrf_ex = re.findall('"(.*?)"', vprn_export)
        else:
            vrf_ex = vprn_export
        vprn_dict.update({vprn_id: {
            'description': vprn_desc,
            'customer': vprn_cust,
            'service-name': vprn_name,
            'vrf-import': vrf_im,
            'vrf-export': vrf_ex,
            'as': vprn_as,
            'rd': vprn_rd,
            'vrf-target': vprn_target,
            'autobind': vprn_autobind,
            'res_filter': vprn_res_filter,
            'res_gre': vprn_res_gre,
            'res_ldp': vprn_res_ldp,
            'res_rsvp': vprn_res_rsvp,
        }})
        if vprn_dict:
            return vprn_dict

    def vprn_ifaces(self, vprn_sect):
        '''returns all ifaces configured on the vprn'''
        vprn_ifaces = re.findall('[\r\n]+[ ]{12}interface "(.*)" create', vprn_sect)
        return vprn_ifaces

    def iface_parms(self, iface_list, vprn_sect):
        '''returns dictionary of all iface parameters'''
        iface_dict = {}
        for iface in iface_list:
            iface_sect = self._find_section(12, 'interface "{}"'.format(iface), vprn_sect)
            iface_name = self._search_func('[\r\n]+[ ]{12}interface "(.*)" create', iface_sect)
            iface_desc = self._search_func('[\r\n]+[ ]{16}description "(.*)"', iface_sect)
            iface_address = self._search_func('[\r\n]+[ ]{16}address (\d+.\d+.\d+.\d+/\d+)', iface_sect)
            iface_address_sec = re.findall('[\r\n]+[ ]{16}secondary (\d+.\d+.\d+.\d+/\d+)', iface_sect)
            iface_spoke_sdp = self._search_func('[\r\n]+[ ]{16}spoke-sdp (\d+:\d+)', iface_sect)
            iface_ip_mtu = self._search_func('[\r\n]+[ ]{16}ip-mtu (\d+)', iface_sect)
            iface_state = self._search_func('[\r\n]+[ ]{16}(no shutdown)', iface_sect)
            iface_mac = self._search_func('[\r\n]+[ ]{16}mac (.*)', iface_sect)
            try:
                iface_sap_id = self._search_func('[\r\n]+[ ]{16}sap (.*) create', iface_sect)
                iface_sap = self.sap_parms([iface_sap_id], iface_sect)[iface_sap_id]
            except Exception as f:
                print ('{}'.format(f))
                iface_sap_id = False
                iface_sap = False
            iface_dict.update({iface: {
                'name': iface_name,
                'description': iface_desc,
                'address': iface_address,
                'address_sec': iface_address_sec,
                'spoke_sdp': iface_spoke_sdp,
                'mtu': iface_ip_mtu,
                'state': iface_state,
                'mac': iface_mac,
                'sap_id': iface_sap_id,
                'sap': iface_sap
            }})
        if iface_dict:
            return iface_dict


class VplsParms(ServiceSlicing):
    def __init__(self, service_section):
        self.service_section = service_section

    def vpls_list(self, service_section):
        '''returns all vpls IDs configured on the node'''
        vpls_ids = re.findall('[\r\n]+[ ]{8}vpls (\d+) customer', service_section)
        return vpls_ids

    def vpls_section(self, vpls_id, service_section):
        vpls_sect = self._find_section(8, 'vpls', service_section, vpls_id)
        return vpls_sect

    def vpls_parms(self, vpls_list, vpls_sect):
        '''returns dictionary of all vpls-s and related parameters'''
        vpls_dict = {}
        for vpls_id in vpls_list:
            vpls_cust = self._search_func('vpls \d+ customer (\d+)', vpls_sect)
            vpls_desc = self._search_func('[\r\n]+[ ]{12}description "(.*)"', vpls_sect)
            vpls_name = self._search_func('[\r\n]+[ ]{12}service-name "(.*)"', vpls_sect)
            vpls_fdb_size = self._search_func('[\r\n]+[ ]{12}fdb-table-size (.*)', vpls_sect)
            vpls_local_age = self._search_func('[\r\n]+[ ]{12}local-age (.*)', vpls_sect)
            vpls_remote_age = self._search_func('[\r\n]+[ ]{12}remote-age (\d+)', vpls_sect)
            vpls_end = self._search_func('[\r\n]+[ ]{12}endpoint "(.*)" create', vpls_sect)
            end_sect = self._find_section(12, 'endpoint', vpls_sect)
            end_signaling = self._search_func('[\r\n]+[ ]{16}(.*suppress-standby-signaling)', end_sect)
            end_revert = self._search_func('[\r\n]+[ ]{16}revert-time (.*)', end_sect)
            stp_sect = self._find_section(12, 'stp', vpls_sect)
            stp_state = self._search_func('[\r\n]+[ ]{12}(no shutdown)', stp_sect)
            vpls_s_f_o_failure = self._search_func('[\r\n]+[ ]{12}(send-flush-on-failure)', vpls_sect)
            vpls_sdps = re.findall('[\r\n]+[ ]{12}((?:(?:mesh)|(?:spoke))-sdp.*) create', vpls_sect)
            vpls_dict.update({vpls_id: {
                'customer': vpls_cust,
                'description': vpls_desc,
                'service-name': vpls_name,
                'fdb-size': vpls_fdb_size,
                'local-age': vpls_local_age,
                'remote-age': vpls_remote_age,
                'endpoint': vpls_end,
                'standby-signal': end_signaling,
                'revert-time': end_revert,
                'stp_state': stp_state,
                'send-flush': vpls_s_f_o_failure,
                'sdp-s': vpls_sdps
            }})
        if vpls_dict:
            return vpls_dict


class PolicyParms(ServiceSlicing):

    def _policy_sect_slice(self):
        '''finds policy section in the conf file'''
        try:
            policy_start = self.config.index('echo "Policy Configuration"')
        except Exception as f:
            print ('Error: {}'.format(f))
        else:
            section_end = '\n        exit'
            pol_section = self.config[policy_start:]
            try:
                policy_section = pol_section[:pol_section.index(section_end)]
            except Exception as f:
                print ('Error: {}'.format(f))
            else:
                return policy_section

    def policy_list(self, policy_section):
        '''returns all policy names configured on the node'''
        policy_names = re.findall('[\r\n]+[ ]{12}policy-statement '
                                  '"(.*)"', policy_section)
        return policy_names

    def prefix_list(self, policy_section):
        '''returns all prefix-lists configured on the node'''
        prefix_lists = re.findall('[\r\n]+[ ]{12}prefix-list '
                                  '"(.*)"', policy_section)
        return prefix_lists

    def community_dict(self, policy_section):
        '''returns all communities configured on the node'''
        community_lists = re.findall('[\r\n]+[ ]{12}(community '
                                     '".*" members ".*")', policy_section)
        community_dict = {}
        for com in community_lists:
            com.rstrip()
            try:
                com_name = re.match(r'community "(.*)" members ".*"', com).group(1)
                members = re.match(r'community ".*" members "(.*)"', com).group(1)
            except Exception as f:
                print(f)
            else:
                community_dict[com_name] = members
        return community_dict

    def prefix_section(self, prefix_name, policy_section):
        prefix_sect = self._find_section(12, 'prefix-list',
                            policy_section, '"{}"'.format(prefix_name))
        return prefix_sect

    def prefix_dict(self, prefix_list, policy_section):
        '''returns prefix-lists dict'''
        prefix_dict = {}
        for p_name in prefix_list:
            p_sec = self.prefix_section(p_name, policy_section)
            prefixes = re.findall(r'prefix (.*)', p_sec)
            r_prefixes = [x.rstrip() for x in prefixes]
            prefix_dict[p_name] = r_prefixes
        return prefix_dict

    def pol_section(self, policy_name, policy_section):
        policy_sect = self._find_section(12, 'policy-statement',
                                policy_section, '"{}"'.format(policy_name))
        return policy_sect

    def policy_dict(self, policy_list, policy_section):
        '''returns policy-lists dict'''
        policy_dict = {}
        for p_name in policy_list:
            p_sec = self.pol_section(p_name, policy_section)
            policy_dict[p_name] = p_sec
        return policy_dict

    def policy_parms(self, pol_conf):
        prefixes = re.findall(r'prefix-list "(.*)"', pol_conf)
        r_prefixes = set(prefixes)
        comms = re.findall(r'community "(.*)"', pol_conf)
        comms.extend(re.findall(r'community add "(.*)"', pol_conf))
        r_comms = set(comms)
        return {'prefixes': list(r_prefixes),
                'communities': list(r_comms)}

