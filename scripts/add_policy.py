#!/usr/bin/env python
# adam radford aradford@cisco.com
# this is sample code, purpose to illustrate use of the APIC-EM API
#
# run as
# python policy.py
#

import requests
import json
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
        return response.status_code

policy = {
  "policyOwner": "Admin",
  "networkUser": {"userIdentifiers":["40.0.0.15"],
                    "applications":[{"raw": "12340;UDP"}]},
  "actionProperty": {"priorityLevel": "46"},
  "actions": ["PERMIT"],
  "policyName": "voice:audio:40.0.0.15-%s" % GROUP
}


# add the policy
res = rest_call("/policy", "POST", policy)
if res is not None:
    # get the task for policy creation
    task_id = res['response']['taskId']

    # print the response with the task
    print json.dumps(res, indent=4, separators=(',', ': '))
    print "sleeping for task to complete"
    time.sleep(3)
    
    # get the results of the task
    task_res = rest_call("/task/%s" % task_id, "GET", "")

    # print the result of the task
    print json.dumps(task_res['response'], indent=4, separators=(',', ': '))

