Linux
python3 run_migration_flow.py

Windows
py .\run_migration_flow.py

pip install -r requirements.txt

Requirements
User will need an Azure Subscription and Resource Group
User will need Contributor role to that subscription/resource group
Your Azure user will need console access to Azure Migration Tooling

You will need to create a dynatrace API Token with entities.read and metrics.read

We recommend you spin up an azure linux virtual machine as that is what the code has been tested on

To Run:
Update information in the inputs.py
python3 run_migrate_flow.py
