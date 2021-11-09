#!/usr/bin/env python

######################################################################################################
# LLLLLLLLLLL                            AAA               ZZZZZZZZZZZZZZZZZZZEEEEEEEEEEEEEEEEEEEEEE #
# L:::::::::L                           A:::A              Z:::::::::::::::::ZE::::::::::::::::::::E #
# L:::::::::L                          A:::::A             Z:::::::::::::::::ZE::::::::::::::::::::E #
# LL:::::::LL                         A:::::::A            Z:::ZZZZZZZZ:::::Z EE::::::EEEEEEEEE::::E #
#   L:::::L                          A:::::::::A           ZZZZZ     Z:::::Z    E:::::E       EEEEEE #
#   L:::::L                         A:::::A:::::A                  Z:::::Z      E:::::E              #
#   L:::::L                        A:::::A A:::::A                Z:::::Z       E::::::EEEEEEEEEE    #
#   L:::::L                       A:::::A   A:::::A              Z:::::Z        E:::::::::::::::E    #
#   L:::::L                      A:::::A     A:::::A            Z:::::Z         E:::::::::::::::E    #
#   L:::::L                     A:::::AAAAAAAAA:::::A          Z:::::Z          E::::::EEEEEEEEEE    #
#   L:::::L                    A:::::::::::::::::::::A        Z:::::Z           E:::::E              #
#   L:::::L         LLLLLL    A:::::AAAAAAAAAAAAA:::::A    ZZZ:::::Z     ZZZZZ  E:::::E       EEEEEE #
# LL:::::::LLLLLLLLL:::::L   A:::::A             A:::::A   Z::::::ZZZZZZZZ:::ZEE::::::EEEEEEEE:::::E #
# L::::::::::::::::::::::L  A:::::A               A:::::A  Z:::::::::::::::::ZE::::::::::::::::::::E #
# L::::::::::::::::::::::L A:::::A                 A:::::A Z:::::::::::::::::ZE::::::::::::::::::::E #
# LLLLLLLLLLLLLLLLLLLLLLLLAAAAAAA                   AAAAAAAZZZZZZZZZZZZZZZZZZZEEEEEEEEEEEEEEEEEEEEEE #
######################################################################################################

# for CDK
from constructs import Construct
from cdktf import App, NamedRemoteWorkspace, TerraformOutput, TerraformStack, TerraformHclModule, RemoteBackend

# for terraform provider
from cdktf_cdktf_provider_aws import AwsProvider, AwsProviderDefaultTags, AwsProviderAssumeRole
from cdktf_cdktf_provider_aws.organizations import OrganizationsOrganization, DataAwsOrganizationsOrganization, OrganizationsOrganizationalUnit, OrganizationsPolicy, OrganizationsPolicyAttachment, OrganizationsAccount
from cdktf_cdktf_provider_aws.data_sources import DataAwsAvailabilityZones
from cdktf_cdktf_provider_aws.iam import IamAccountAlias

# general
import yaml
import os
import sys

from entities.Account import Account
from entities.Policy import Policy
from entities.OrganizationalUnit import OrganizationlUnit
from entities.TerraformModule import TerraformModule
from entities.GlobalConfig import GlobalConfig

######################### DEFAULTS #########################
ASSUME_ROLE_NAME = 'OrganizationAccountAccessRole'
############################################################

######################### MODULES #########################
LOCAL_MODULES_SOURCE = f'./modules'
AWS_VPC_MODULE_SOURCE = 'terraform-aws-modules/vpc/aws'
AWS_VPC_MODULE_VERSION = '3.7.0'
###########################################################

class LazeStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        self._config = self.__get_config_obj(os.environ.get('CONFIG_FILE_PATH'))
        self.__register_param_classes()

        # Get default tags
        provider_default_tags = AwsProviderDefaultTags(tags=self.global_config.global_tags)

        region = self.global_config.region
        profile = self.global_config.aws_profile

        AwsProvider(self, 'aws-root', region=region, profile=profile, default_tags=provider_default_tags)

        ### Set IAM alias for root account ###
        if self.global_config.root_account_alias != "":
            IamAccountAlias(self, 'alias', account_alias=self.global_config.root_account_alias)

        ### Create organization ###
        if self.global_config.create_organization is True:
            organization_resource = OrganizationsOrganization(self, 'org',
                                                              feature_set='ALL',
                                                              enabled_policy_types=['SERVICE_CONTROL_POLICY', 'TAG_POLICY', 'BACKUP_POLICY'])
        else:
            organization_resource = DataAwsOrganizationsOrganization(self, 'organization')

        ### Create policies ###
        for policy in self.policies_instances:
            policy_name = policy.name
            policy_resource = OrganizationsPolicy(self, policy_name, depends_on=[organization_resource], type=policy.type, name=policy_name, content=policy.content)
            policy.id = policy_resource.id

        ### Create organizational units ###
        for ou in self.organizational_units_instances:
            ou_name = ou.name
            parent_ou = ou.parent_ou

            # Get the ID of the parent OU
            if parent_ou != "":
                parent_ou_id = self.get_ou_by_name(parent_ou).id
            else:
                parent_ou_id = organization_resource.roots('0').id

            organizational_unit_resource = OrganizationsOrganizationalUnit(self, ou_name, name=ou_name, parent_id=parent_ou_id)
            ou.id = organizational_unit_resource.id

            # Attach policies to the OU
            for policy in ou.policies:
                OrganizationsPolicyAttachment(self, f'{ou_name}-{policy}', policy_id=self.get_policy_by_name(policy).id, target_id=organizational_unit_resource.id)

        ### Get all availability zones ###
        azs = sorted(DataAwsAvailabilityZones(self, 'azs', state='available').names)

        ### Create new accounts ###
        for account in self.accounts_instances:
            account_name = account.name
            account_resource = OrganizationsAccount(self, account_name, depends_on=[organization_resource], name=account_name, email=account.email, parent_id=self.get_ou_by_name(account.ou).id)
            account.id = account_resource.id

            # Attach policies to the account
            for policy in account.policies:
                OrganizationsPolicyAttachment(self, f'{account_name}-{policy}', policy_id=self.get_policy_by_name(policy).id, target_id=account_resource.id)

            # Create provider to deploy resoruces in the new account
            provider = AwsProvider(self, f'aws-{account_name}',
                                   alias=f'aws-{account_name.replace(" ", "")}',
                                   region=region,
                                   profile=profile,
                                   default_tags=provider_default_tags,
                                   assume_role=AwsProviderAssumeRole(role_arn = f'arn:aws:iam::{account_resource.id}:role/{ASSUME_ROLE_NAME}'))
            account.provider = provider

            # Create network in new account
            # TODO: Might need to add "sleep" before deploying to accounts (https://github.com/hashicorp/terraform-cdk/issues/323)
            network_config = account.network
            if len(network_config.keys()) > 0:
                TerraformHclModule(self, f'{account_name}-network',
                                source=AWS_VPC_MODULE_SOURCE,
                                version=AWS_VPC_MODULE_VERSION,
                                providers=[provider],
                                depends_on=[organization_resource],
                                variables={
                                    'name': network_config['name'],
                                    'cidr': network_config['vpc_cidr'],
                                    'azs': azs[0:max(len(network_config['public_subnets'] if 'public_subnets' in network_config else []),
                                                        len(network_config['private_subnets'] if 'private_subnets' in network_config else []))],
                                    'public_subnets': network_config['public_subnets'] if 'public_subnets' in network_config else [],
                                    'private_subnets': network_config['private_subnets'] if 'private_subnets' in network_config else [],
                                })

            if 'audit' in account.roles:
                audit_account_id = account.id
            if 'log_archive' in account.roles:
                log_archive_account_id = account.id

        ### Deploy management resources ###
        # Deploy management resources using Terraform
        # TODO: Improve the management accounts to not rely on each other
        # TODO: Might need to add "sleep" before deploying to accounts (https://github.com/hashicorp/terraform-cdk/issues/323)
        for account in self.accounts_instances:
            if 'audit' in account.roles:
                TerraformHclModule(self, 'audit-module',
                                    source=f'{LOCAL_MODULES_SOURCE}/audit',
                                    providers=[account.provider],
                                    depends_on=[organization_resource],
                                    variables={
                                        'managed_resource_prefix': 'aws-controltower', # TODO: Replace with ts-laze (or other)
                                        'log_archive_account_id': log_archive_account_id,
                                    })
            if 'log_archive' in account.roles:
                TerraformHclModule(self, 'log-archive-module',
                                    source=f'{LOCAL_MODULES_SOURCE}/log-archive',
                                    providers=[account.provider],
                                    depends_on=[organization_resource],
                                    variables={
                                        'managed_resource_prefix': 'aws-controltower', # TODO: Replace with ts-laze (or other)
                                        'audit_account_id': audit_account_id,
                                    })

        ### Deploy custom Terraform modules on accounts ###
        # TODO: Might need to add "sleep" before deploying to accounts (https://github.com/hashicorp/terraform-cdk/issues/323)
        for tf_module in self.terraform_modules_instances:
            for account_name in tf_module.accounts:
                account = self.get_account_by_name(account_name)
                if account != None:
                    TerraformHclModule(self, f'{account_name}-{tf_module.name}',
                                        source=tf_module.source,
                                        version=tf_module.version,
                                        providers=[account.provider],
                                        depends_on=[organization_resource],
                                        variables=tf_module.variables)

    # Get configuration object
    def __get_config_obj(self, path):
        # Check if path is None (if the environment variable is not set)
        if not path:
            print('[ERROR] Please set the value of CONFIG_FILE_PATH environment variable to the path of the config file')
            sys.exit(2)

        try:
            with open(path, 'r') as config:
                try:
                    return(yaml.safe_load(config))
                except yaml.YAMLError as e:
                    print(e)
                    sys.exit(2)

        except FileNotFoundError as e:
            print(e)
            sys.exit(2)

    def __register_param_classes(self):
        self.global_config = GlobalConfig(self._config)

        self.policies_instances = []
        policies_config = self._config['policies'] if 'policies' in self._config else None
        if policies_config:
            [self.policies_instances.append(Policy(policy)) for policy in policies_config]

        self.organizational_units_instances = []
        organizational_units_config = self._config['organizational_units'] if 'organizational_units' in self._config else None
        if organizational_units_config:
            [self.organizational_units_instances.append(OrganizationlUnit(ou)) for ou in organizational_units_config]

        self.accounts_instances = []
        accounts_config = self._config['accounts'] if 'accounts' in self._config else None
        if accounts_config:
            [self.accounts_instances.append(Account(acc)) for acc in accounts_config]

        self.terraform_modules_instances = []
        terraform_modules_config = self._config['tf_modules'] if 'tf_modules' in self._config else None
        if terraform_modules_config:
            [self.terraform_modules_instances.append(TerraformModule(module)) for module in terraform_modules_config]

    def get_policy_by_name(self, name):
        for policy in self.policies_instances:
            if policy.name == name:
                return policy
        return None

    def get_ou_by_name(self, name):
        for ou in self.organizational_units_instances:
            if ou.name == name:
                return ou
        return None

    def get_account_by_name(self, name):
        for account in self.accounts_instances:
            if account.name == name:
                return account
        return None


app = App()
stack = LazeStack(app, "laze")
RemoteBackend(stack,
  hostname='app.terraform.io',
  organization='TeraSky',
  workspaces=NamedRemoteWorkspace('TeraSky-LAZE')
)

app.synth()
