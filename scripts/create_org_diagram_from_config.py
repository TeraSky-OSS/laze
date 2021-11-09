#!/usr/bin/env python

import sys
import yaml

from diagrams import Cluster, Diagram
from diagrams.aws.management import OrganizationsOrganizationalUnit, OrganizationsAccount
from diagrams.aws.security import IdentityAndAccessManagementIamPermissions

def get_config_resource_by_name(config_resource_list, name):
    for resource in config_resource_list:
        if resource['name'] == name:
            return resource
    return None

if len(sys.argv) != 2:
    print('Please provide exactly one argument with the path to the YAML config file')
    sys.exit(1)

file_path = sys.argv[1]
with open(file_path, "r") as file:
    try:
        config = yaml.safe_load(file)
        print(config)

        with Diagram("Example 1", show=False):
            # Create diagram resources
            with Cluster("OUs"):
                for ou in config['organizational_units']:
                    ou['object'] = OrganizationsOrganizationalUnit(ou['name'])

            for policy in config['policies']:
                policy['object'] = IdentityAndAccessManagementIamPermissions(policy['name'])
            
            with Cluster("Accounts"):
                for account in config['accounts']:
                    account['object'] = OrganizationsAccount(account['name'])

            # Add diagram connections
            for ou in config['organizational_units']:
                if 'parent_ou' in ou:
                    ou['object'] >> get_config_resource_by_name(config['organizational_units'], ou['parent_ou'])['object']
                if 'policies' in ou:
                    for policy in ou['policies']:
                        ou['object'] << get_config_resource_by_name(config['policies'], policy)['object']
            
            for account in config['accounts']:
                account['object'] >> get_config_resource_by_name(config['organizational_units'], account['ou'])['object']
                if 'policies' in account:
                    for policy in account['policies']:
                        account['object'] << get_config_resource_by_name(config['policies'], policy)['object']

    except yaml.YAMLError as exc:
        print(exc)