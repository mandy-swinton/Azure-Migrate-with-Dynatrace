from azure.cli.core import get_default_cli
from get_dynatrace_data import gather_dyantrace_data
import json
import subprocess
import os
import time
from inputs import SUBSCRIPTION_ID, RESOURCE_GROUP, MIGRATION_PROJECT_NAME, AZ_TENANT_ID, BUSINESS_CASE_NAME, AZURE_REGION, CURRENCY


def az_cli (args_str):
    args = args_str.split()
    cli = get_default_cli()
    cli.invoke(args)
    if cli.result.result:
        return cli.result.result
    elif cli.result.error:
        raise cli.result.error
    return True


subscription_id = SUBSCRIPTION_ID
resource_group = RESOURCE_GROUP
migration_project_name = MIGRATION_PROJECT_NAME
azure_region = AZURE_REGION
business_case_name = BUSINESS_CASE_NAME
currency = CURRENCY

def run_azure_migrate():
    headers = '{"Content-Type":"application/json"}'

    import_site_name = "dynatrace-import-site"
    master_site_name = "dynatrace-master-site"
    solution_name = "assessment_solution_dt"
    file_path = "dyna_output.csv"

    login()
    
    #create_migration_project(subscription_id, resource_group, migration_project_name, headers)
    #create_assessment_project(subscription_id,resource_group,migration_project_name, azure_region, headers)
    #######attach_solutions(subscription_id,resource_group,migration_project_name, solution_name, headers)
    #create_import_site(subscription_id, resource_group, migration_project_name, azure_region, import_site_name, headers)
    #update_migrate_project(subscription_id, resource_group, import_site_name, migration_project_name)
    #update_master_site(subscription_id,resource_group,master_site_name, import_site_name, azure_region, migration_project_name, headers)
    #upload_uri, job_id = get_sas_uri_for_import(subscription_id,resource_group,import_site_name)
    #upload_dynatrace_data(file_path, upload_uri)
    #get_upload_status(subscription_id, resource_group, import_site_name, job_id)
    #get_imported_machines(subscription_id,resource_group, import_site_name)
    assessment_project_name = get_assessment_name(subscription_id,resource_group, migration_project_name, headers)
    #assessment_project_name = "test-proj-name-dt"
    
    #create_business_case(business_case_name, azure_region, currency,subscription_id,resource_group, migration_project_name, headers)
    #get_business_case(subscription_id,resource_group, migration_project_name, business_case_name)
    #get_evaluated_machines(subscription_id,resource_group,migration_project_name,business_case_name)


def login():
    az_login = f"login --tenant {AZ_TENANT_ID}"
    response = az_cli(az_login)

def create_migration_project(subscription_id, resource_group, migration_project_name, headers):
    print("CREATING MIGRATION PROJECT")
    body_json ='{"properties":{},"location":"westus2","tags":{}}'
   
    create_migrate_project_url = f'rest --method PUT --url https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Migrate/migrateProjects/{migration_project_name}?api-version=2018-09-01-preview --headers {headers} --body {body_json}'

    response = az_cli(create_migrate_project_url)
    print("CREATE MIGRATION RESPONSE: ", response)

def create_assessment_project(subscription_id,resource_group,migration_project_name, azure_region, headers):
    print("CREATE ASSESSMENT PROJECT")
    assessment_solution_id = f'/subscriptions/{subscription_id}/resourcegroups/{resource_group}/providers/microsoft.migrate/migrateprojects/{migration_project_name}/Solutions/Servers-Assessment-ServerAssessment'
    create_assessment_body = '{"properties":{"assessmentSolutionId":"'+assessment_solution_id+'","projectStatus":"Active","customerWorkspaceId":null,"customerWorkspaceLocation":null},"eTag":"","location":"'+azure_region+'","tags":{}}'
    create_assessment_url = f'rest --method PUT --url https://management.azure.com/subscriptions/{subscription_id}/resourcegroups/{resource_group}/providers/Microsoft.Migrate/assessmentProjects/{migration_project_name}?api-version=2019-10-01 --headers {headers} --body {create_assessment_body}'
    print(az_cli(create_assessment_url))

def attach_solutions(subscription_id,resource_group,migration_project_name, solution_name, headers):
    solution_body = '{"properties":{"tool":"ServerAssessment","purpose":"Assessment","goal":"Servers"}}'
    attach_solution_url = f'rest --method PUT --url https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Migrate/migrateProjects/{migration_project_name}/solutions/{solution_name}?api-version=2018-09-01-preview --headers {headers} --body {solution_body}'
    print(az_cli(attach_solution_url))


def create_import_site(subscription_id, resource_group, migration_project_name, azure_region, import_site_name, headers):
    #create import site
    print("CREATING IMPORT SITE")
    
    discovery_solution_id = f"subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Migrate/MigrateProjects/{migration_project_name}/Solutions/Servers-Discovery-ServerDiscovery_Import"
    import_site_body ='{"type":"microsoft.offazure/importsites","name":"'+import_site_name+'","location":"'+azure_region+'","properties":{"discoverySolutionId":"'+discovery_solution_id+'"}}'
    import_site_url = f'rest --method PUT --url https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/microsoft.offazure/importsites/{import_site_name}?api-version=2019-05-01-preview  --headers {headers} --body {import_site_body}'
    response = az_cli(import_site_url)
    print("IMPORT SITE RESPONSE: ", response)

def update_migrate_project(subscription_id, resource_group, import_site_name, migration_project_name):
    print("UPDATE MIGRATE PROJECT")
    import_site_id = f'"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/microsoft.offazure/importsites/{import_site_name}"'
    update_migrate_project_body = '{"type":"Microsoft.Migrate/MigrateProjects/Solutions","apiVersion":"2020-06-01-preview","name":"'+migration_project_name+'/Servers-Discovery-ServerDiscovery_Import","properties":{"tool":"ServerDiscovery_Import","purpose":"Discovery","goal":"Servers","status":"Active","details":{"extendedDetails":{"importSiteId":'+import_site_id+'}}}}'
    update_migrate_project_url = f'rest --method PUT --url https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Migrate/MigrateProjects/{migration_project_name}/Solutions/Servers-Discovery-ServerDiscovery_Import?api-version=2020-06-01-preview --body {update_migrate_project_body}'
    response = az_cli(update_migrate_project_url)
    print("UPDATE MIGRATE RESPONSE: ", response)

def update_master_site(subscription_id,resource_group,master_site_name, import_site_name, azure_region, migration_project_name, headers):
    sites = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/microsoft.offazure/importsites/{import_site_name}"
    update_master_site_body ='{"type":"Microsoft.OffAzure/MasterSites","name":"'+master_site_name+'","location":"'+azure_region+'","tags":{"MigrateProject":"'+migration_project_name+'"},"kind":"Migrate","properties":{"sites":["'+sites+'"],"allowMultipleSites":true}}'
    print(update_master_site_body)
    update_master_site_url = f'rest --method PUT --url https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.OffAzure/MasterSites/{master_site_name}?api-version=2020-07-07 --headers {headers} --body {update_master_site_body}'
    update_master_site_url = f'rest --method GET --url https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.OffAzure/MasterSites/{master_site_name}?api-version=2020-07-07'
    response = az_cli(update_master_site_url)
    print("UPDATE MASTER SITE RESPONSE: ", response)

def get_sas_uri_for_import(subscription_id,resource_group,import_site_name):
    print("CREATE SAS URI FOR IMPORT")
    get_SAS_URI_for_input_url = f"rest --method POST --url https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/microsoft.offazure/importsites/{import_site_name}/ImportUri?api-version=2019-05-01-preview"
    response = az_cli(get_SAS_URI_for_input_url)
    upload_uri = response["uri"]
    job_arm_id = response["jobArmId"]
    job_id = job_arm_id.split("/jobs/")[1]
    #print(job_id)
    print("CREATE SAAS URI FOR IMPORT RESPONSE: ", response)
    return upload_uri, job_id

def upload_dynatrace_data(file_path, upload_uri):
    print("UPLOAD DYNATRACE DATA")
    #TODOL UNCOMMENT TO RUN DYNATRACE CODE
    upload_body = gather_dyantrace_data().replace(" ","%20").replace("\n","%0A")
    upload_url = f"az storage blob upload -f {file_path} --blob-url '{upload_uri}'"
    #run outside the venv because of the way credentials are stored
    process = subprocess.run(['bash', '--login', '-c',upload_url], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={})
    print("UPLOAD BLOB REPONSE ",process)
    print("WAITNG 10 SECONDS FOR DATA TO PROCESS")
    time.sleep(10)

def get_upload_status(subscription_id, resource_group, import_site_name, job_id):
    get_upload_status = f"rest --method GET --url https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.OffAzure/ImportSites/{import_site_name}/jobs/{job_id}?api-version=2019-05-01-preview"
    upload_status = az_cli(get_upload_status)
    print(upload_status)

    #job_statuses = ["Unknown","Completed","CompletedWithWarnings","CompletedWithErrors","Failed","WaitingForBlobUpload","InProgress"]
    
    while "Completed" not in upload_status["status"]:
        if upload_status["status"] == "Failed":
            print("UPLOAD FAILED, PLEASE CHECK DATA AND TRY AGAIN")
            exit()
            
        print("Job Status: ", upload_status["status"])
        print("Hang tight, will recheck in 10 seconds")
        time.sleep(10)
        upload_status = az_cli(get_upload_status)

    
    print("Job Status: ", upload_status['properties']['jobResult'] )

def get_imported_machines(subscription_id,resource_group, import_site_name):
    print("GET IMPORTED MACHINES")
    get_imported_machines = f"rest --method GET --url https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.OffAzure/ImportSites/{import_site_name}/machines?api-version=2019-05-01-preview"
    print(az_cli(get_imported_machines))

def get_assessment_name(subscription_id,resource_group, migration_project_name, headers):
    print("GET ASSESSMENT NAME")
    get_assessment_url = f'rest --method GET --url https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Migrate/MigrateProjects/{migration_project_name}/Solutions/Servers-Assessment-ServerAssessment?api-version=2020-06-01-preview --headers {headers}'
    
    assement_response = az_cli(get_assessment_url)
    project_id = assement_response["properties"]["details"]["extendedDetails"]["projectId"]
    project_id_split = project_id.split("/")
    assessment_project_name = project_id_split[len(project_id_split)-1]
    print(assessment_project_name)
    return assessment_project_name
    

def create_business_case(business_case_name, azure_region, currency,subscription_id,resource_group, migration_project_name, headers):
    print("CREATE BUSINESS CASE")
   
    business_case_body = '{"properties":{"settings":{"azureSettings":{"targetLocation":"'+azure_region+'","currency":"'+currency+'","businessCaseType":"IaaSOnly","workloadDiscoverySource":"Import"}}}}' #,id": "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Migrate/AssessmentProjects/{assessment_project_name}/BusinessCases/{business_case_name},"name": "{business_case_name}", "type": "Microsoft.Migrate/assessmentprojects/businesscases","systemData": null CLOSE'

    create_business_case_url = f'rest --method PUT --url https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Migrate/AssessmentProjects/{migration_project_name}/BusinessCases/{business_case_name}?api-version=2023-09-09-preview  --headers {headers} --body {business_case_body} --debug'
    print(az_cli(create_business_case_url))

def get_business_case(subscription_id,resource_group, migration_project_name, business_case_name):
    get_business_case_url = f'rest --method GET --url https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Migrate/AssessmentProjects/{migration_project_name}/BusinessCases/{business_case_name}?api-version=2023-09-09-preview'
    print(az_cli(get_business_case_url))

def get_evaluated_machines(subscription_id,resource_group,migration_project_name,business_case_name):
    get_evaluated_machines_url = f'rest --method GET --url https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Migrate/AssessmentProjects/{migration_project_name}/BusinessCases/{business_case_name}/evaluatedMachines?api-version=2023-09-09-preview&pageSize=20'
    print(az_cli(get_evaluated_machines_url))

run_azure_migrate()