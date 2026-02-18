from olca_client import OLCAClient

client = OLCAClient(port=8080)

unit_group_names = [ug.name for ug in client.get_all_unit_groups()]

print(unit_group_names)

print(client.get_flow("1-Pentene"))