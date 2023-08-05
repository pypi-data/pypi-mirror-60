from azure.keyvault.secrets import SecretClient
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.compute import ComputeManagementClient

class AzureKeyvaultHelper:
    def __init__(self, key_vault_name: str):
        self.key_vault_uri = "https://" + key_vault_name + ".vault.azure.net"

    def get_secret(self, secret_name: str):
        credential = get_client_from_cli_profile(ComputeManagementClient).config.credentials
        client = SecretClient(self.key_vault_uri, credential)
        return client.get_secret(secret_name).value

    def set_secret(self, secret_name: str, secret_value):
        credential = get_client_from_cli_profile(ComputeManagementClient).config.credentials
        client = SecretClient(self.key_vault_uri, credential)
        client.set_secret(secret_name, secret_value)
