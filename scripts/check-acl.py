#!/usr/bin/python
# adam radford aradford@cisco.com
# This is sample code only
# Illustrates the use of the APIC-EM API

import time
import requests
import json
from apic import APIC_IP, APIC_PORT

IP = "test-apic"
BASE = "/api/v0"

# how to make REST call to controller.  Note need to set verify=False for SSL   
def rest_call(url, action, data):
    #call_url = "http://" + IP + BASE + url
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
        
        response = requests.post(url=call_url,data=body, headers=headers, verify=False)

        # either 201 or 207, policy returns a partial 207
        print response.status_code
        if response.status_code != 409:
            return response.json()
        else:
            return None
    elif action == "DELETE":
        response = requests.delete(url=call_url, verify=False)
        return response.status_code



'''
     "deviceName": "ZTD-router",
      "deviceId": "401a7b75-f7fb-4a20-8e8b-1348a2954d77",
      "interfaceName": "GigabitEthernet0/1",
      "interfaceID": "f0864fe9-614c-4186-8605-31059d9b4217",
      "aclModules": [
        {
          "acl": {
            "id": "eda11d98-311d-40f0-b30e-acd281d1d186",
            "name": "100",
            "type": "EXTENDED",
            "refcount": 2,
'''

# format the fail message
def format_fail(acl_fail):
#    #Step2: Change the output to just the conflict issue.  ####
    return json.dumps(acl_fail,indent=4, separators=(',', ': '))
    #return json.dumps(acl_fail['conflictList'],indent=4, separators=(',', ': '))
#    #End Step2 ######

# work out if acl check succeeded or not.
def process_result(result):
    # if empty or not present then ok... "conflictList"
    if not 'conflictList' in result:
        return "PASS"
    if result['conflictList'] == []:
        return "PASS"
    else:
       return "FAIL:" + format_fail(result)

# main loop.
# for all devices,
#       grab the ACL
#           for each ACL
#                check it
###
# get all devices
res = rest_call("/network-device/", "GET", "")
if res is not None:
    dev_list = res['response']
    for dev in dev_list:
        dev_id = dev['id']
        dev_name = dev['hostname']
        dev_ip = dev['managementIpAddress']
        print "Checking device:",  dev_name + ":" + dev_ip + ":" + dev_id

        # get the ACL on device
        acl_res = rest_call("/acl/device/" + dev_id, "GET", "")
        if acl_res is not None:
            acl_list = acl_res['response']
            
            # look at each interface
            for acls in acl_list:
                acl_int = acls['interfaceName']

                for acl in acls['aclModules']:
                    print "   INT:%s ACL: %s" % (acl_int, acl['acl']['name']),
                    acl_id = acl['acl']['id']

#                   # Step1 Run the call to look for conflicts ####
                    #res_conf = rest_call("/acl/conflict/" + acl_id, "GET", "")
                    #if res_conf is not None:
                    #    result = res_conf['response']
                    #print process_result(result),
#                   #End of Step 1 ####
                    print
                       
