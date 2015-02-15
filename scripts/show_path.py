#!/usr/bin/env python
# adam radford aradford@cisco.com
# this is sample code, purpose to illustrate use of the APIC-EM API
#
# run as
# python show-path.py
#

import requests
import json
from apic import APIC_IP, APIC_PORT

BASE = "/api/v0"
ID = {}
SRC_IP = "40.0.0.15"
DST_IP = "40.0.5.12"


# how to make REST call to controller.  Note need to set verify=False for SSL
def rest_call(url, action, data):
    #call_url = "https://" + IP + BASE + url
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

    print "\n******\nThis looks like a 'traceroute' but you can",
    print "see interfaces as well as any attributes of the devices"

    # now we do a similar iteration, but look at some more attributes
    # along the path
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
            print "[", end_device['hostname'], "](", end_device['upTime'], ")"
