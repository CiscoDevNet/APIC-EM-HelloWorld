#!/usr/bin/env python
# adam radford aradford@cisco.com
# This is sample code ONLY
# illustrates the use of the APIC-EM API
#
# run as
# python show-path-acl.py
#
import requests
import json
from apic import APIC_IP, APIC_PORT
import logging
logging.captureWarnings(True)

BASE = "/api/v0"
ID = {}
SRC_IP = "40.0.0.15"
DST_IP = "40.0.5.12"


# how to make REST call to controller.  Note need to set verify=False for SSL
def rest_call(url, action, data):
    call_url = "https://%s:%s%s%s" %(APIC_IP, APIC_PORT, BASE, url)
    #print call_url

    if action == "GET":
        response = requests.get(url=call_url, verify=False)

        if response.status_code == 200:
            return response.json()
        else:
            return None
    elif action == "POST":
        headers = {'Content-type': 'application/json'}
        body = json.dumps(data)

        response = requests.post(url=call_url,
                                 data=body, headers=headers, verify=False)

        # either 201 or 207, policy returns a partial 207
        print response.status_code
        if response.status_code != 409:
            return response.json()
        else:
            return None
    elif action == "DELETE":
        response = requests.delete(url=call_url, verify=False)
        return response.status_code

def show_interface(interface):
    '''
     "relevantAces": [
           {
	    "destPortInfoList": [
	        {
	         "protocol": "tcp",
	         "ports": "458"
	        }
	   ],
    '''
    result = interface['interfaceName']
    if interface["aclName"] is not None:
        result += " (%s) block=%s" % (interface['aclName'], interface['blockType'])
    for ace in interface['relevantAces']:
    #    for destport in XXXXXXXXXXXXX
#	    result += "(%s:%s)" % (destport['protocol'], destport['ports'])
        return result
    
def show_device(device):
    interfaces = device['interfaces']
    if interfaces[0]['ingress']:
	ingress = interfaces[0]
        egress = interfaces[1]
    else:
        ingress = interfaces[1]
        egress = interfaces[0]
    result = show_interface(egress)
    result += "\n%s\n" % device['deviceName']
    result += show_interface(ingress)
    return result

def get_byid(table, uuid):
    if uuid == "":
        return None
    rres = rest_call("/" + table + "/" + uuid, "GET", "")
    if rres is not None:
        return rres['response']

    return None

print "looking at path from " + SRC_IP + " to " + DST_IP
# this could be a user parameter, and validated with hosts
res = rest_call("/routing-path/" + SRC_IP + "/" + DST_IP, "GET", "")
if res is not None:
    path = res['response'][0]['links']
    print json.dumps(path, indent=4, separators=(',', ': '))

    print "*******\nShowing the path and interfaces...."
    for node in path:
        start_interface = get_byid("interface", node['startPortID'])
        end_interface = get_byid("interface", node['endPortID'])
        start_device = get_byid("network-device", node['source'])
        end_device = get_byid("network-device", node['target'])

        if start_interface is None:
            start_host = get_byid("host", node['source'])
            print start_host['hostIp'], "->",
        else:
            print "->", start_interface['portName'], "--",
        if end_interface is None:
            end_host = get_byid("host", node['target'])
            print end_host['hostIp']
        else:
            print end_interface['portName'], "->",
            print end_device['hostname'],

    print "\n******\nNow collect NODES and LINKS to do ACL-path"

    node_list = res['response'][0]['nodes']
    link_list = res['response'][0]['links']
    node_ids = [n['id'] for n in node_list]
    #print node_ids
    
    link_ids = []
    for l in link_list:
        link_ids.append(l['startPortID'])
        link_ids.append(l['endPortID'])
    #print link_ids
        
    acl_req = {
        "applicationId":"46de799b-7f51-4a5e-8d08-46e2e78ff619",
        "interfaceIds": link_ids, # list of ports/interfaces
        "sourceIp": SRC_IP,
        "destIp": DST_IP
        }
 
    print json.dumps(acl_req, indent=4)

    print "RESULT\n******\n"

    post_res = rest_call("/acl/trace", 'POST', acl_req)
    if post_res != None:
        print json.dumps(post_res['response'], indent=4, separators=(',', ': '))
        
# Step1: Look at the devices along the path ######
#        print "\nPATH with ACL"
#        print "%%%%%%%%%%%%%%"
#        for device in post_res['response']['devices']:
#            print show_device(device)
#            print
# End of Step1 #####
