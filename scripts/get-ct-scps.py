#!/usr/bin/env python

import boto3
import json

AWS_PROFILE="ts-playground"
boto3.setup_default_session(profile_name=AWS_PROFILE)

client = boto3.client('organizations')
response = client.list_policies(Filter='SERVICE_CONTROL_POLICY')

full_policy = {"Version": "2012-10-17", "Statement": []}

for policy in response['Policies']:
  if policy['Name'].startswith('aws-guardrails'):
    print(f'Getting policy document for policy {policy["Id"]} ({policy["Name"]})')
    policy_details = client.describe_policy(PolicyId=policy['Id'])
    content = json.loads(policy_details['Policy']['Content'])
    
    full_policy['Version'] = content['Version']
    full_policy['Statement'] = full_policy['Statement'] + content['Statement']

with open("policy.json", "w") as file:
    file.write(json.dumps(full_policy))