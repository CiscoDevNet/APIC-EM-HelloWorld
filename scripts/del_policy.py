#!/usr/bin/env python
# adam radford aradford@cisco.com
# this is sample code, purpose to illustrate use of the APIC-EM API
#
# run as
# python policy.py
#

import requests
import json
import re
import time
from apic import APIC_IP, APIC_PORT, GROUP

BASE = "/api/v0"

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
        return response.json()

print "Delete all of your polices"

res = rest_call("/policy", "GET", "")
if res is not None:
     for policy in res['response']:
	 if re.search(GROUP, policy['policyName']):
             policy_id = policy['id']
	     print "Deleting Policy", json.dumps(policy, indent=4, separators=(',', ': '))

	     del_res = rest_call("/policy/%s" % policy_id, "DELETE", "")
	     task_id = del_res['response']['taskId']
	     print "Result"
	     task_info = rest_call("/task/%s" % task_id, "GET", "")
	     print json.dumps(task_info, indent=4, separators=(',', ': '))

