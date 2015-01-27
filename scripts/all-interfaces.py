#!/usr/bin/env python
# adam radford aradford@cisco.com
# this is sample code, purpose to illustrate use of the APIC-EM API
#
# run as
# python all-interfaces.py
#
from apic import APIC_IP, APIC_PORT
import time
import sys
import signal
import requests
import json
import fileinput
import re
from  netaddr import *

requests.packages.urllib3.disable_warnings() 

BASE="/api/v0"
ID = {}


# how to make REST call to controller.  Note need to set verify=False for SSL   
def rest_call(url, action, data):
    #call_url = "http://" + APIC_IP + BASE + url
    call_url = "https://%s:%s%s%s" %(APIC_IP, APIC_PORT, BASE, url)
    #print call_url
    
    if action == "GET":
        response = requests.get(url = call_url, verify = False)

        if response.status_code == 200:
            return response.json()
        else:
            return None
    elif action == "POST":
        headers = {'Content-type': 'application/json'}
        body = json.dumps(data)
        
        response = requests.post(url=call_url,data=body, headers=headers, verify= False)

        # either 201 or 207, policy returns a partial 207
        print response.status_code
        if response.status_code != 409:
            return response.json()
        else:
            return None
    elif action == "DELETE":
        response = requests.delete(url=call_url, verify = False)
        return response.status_code

# find_element:  allows a lookup of an attribute in a list.  
# For example 'id' in network-device table
def find_element(list, attr, value):
    for l in list:
        if l[attr] == value:
            return l 
    return None

    
# get devices.  Store this table so we can lookup 'id'
device_res = rest_call("/network-device", "GET", "")
if device_res is not None:
    devices = device_res['response']

# get interfaces.  Store this table so we can lookup 'id'
interface_res = rest_call("/interface", "GET", "")
if interface_res is not None:
    interfaces = interface_res['response']

for interface in interfaces:
	if "ipv4Address" in interface:
		print find_element(devices,'id',interface['deviceId'])['hostname'], interface['portName' ], 
			
		# Step1 print the address #####
		# comment out this line 
		#print interface['ipv4Address'] + "/" + interface['ipv4Mask'],
		# End of Step1 #####
		
		#Step2 print out the network subnet ####
		#ip = IPNetwork(interface['ipv4Address'] + "/" + interface['ipv4Mask'])
		#print  ip.network,
		#print interface['status'],
		# end of Step2 #####
	
		print
