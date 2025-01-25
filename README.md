Provide Azure Migrate with Dynatrace Data
The purpose of this set of scripts is to pull your exsisting Dynatrace data and upload it to an Azure Migrate Project

Requirements
User will need an Azure Subscription and Resource Group
User will need Contributor role to that subscription/resource group
Your Azure user will need console access to Azure Migration Tooling

You will need to create a dynatrace API Token with entities.read and metrics.read

To Run
NOTE: This code has been tested on an Azure Linux Virtual Machine. 
It is recommended that you run it on one to avoid environment based conflicts. 



Instructions:
ssh into your VM

git clone https://github.com/mandy-swinton/Azure-Migrate-with-Dynatrace.git 

cd Azure-Migrate-with-Dynatrace

Update information in the inputs.py

    TEST_SUFFIX is just to update if you run it mulitple times, so you don't create Azure objects with the same name

Install Pip: 

    sudo apt-get update

    sudo apt install python3-pip


sudo apt install python3-venv

python3 -m venv .venv

. .venv/bin/activate


pip install -r requirements.txt


python3 run_migrate_flow.py



Need Help?
Email: MicrosoftAlliances@dynatrace.com