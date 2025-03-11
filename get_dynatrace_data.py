import json
import urllib3
from inputs import DT_APIKEY, DT_TENANT
import random
from statistics import quantiles


#TODO: NEXT PAGE KEY
DT_GET_ALL_ENTITIES_URL = DT_TENANT + "/api/v2/entities?entitySelector=type%28%22HOST%22%29"
DT_GET_EACH_ENTITY_URL = DT_TENANT + "/api/v2/entities/"
DT_GET_METRICS_CPU_URL = DT_TENANT + "/api/v2/metrics/query?metricSelector=builtin:host.cpu.usage&from=-14d&to=now&resolution=1h"
DT_GET_METRICS_MEMORY_URL = DT_TENANT + "/api/v2/metrics/query?metricSelector=builtin:host.mem.usage&from=-14d&to=now&resolution=1h"

api_key = f"Api-Token {DT_APIKEY}" 
headers =  headers = {"Authorization": api_key, "Accept": "application/json"}
csv_headers = ["*Server name", "IP addresses","*Cores", "*Memory (In MB)", "*OS name", "OS architecture","CPU utilization percentage","Memory utilization percentage"]

#helper function: make request
def make_http_request(method, url, headers):
    http = urllib3.PoolManager()
    r = http.request(method, url, headers=headers)
    data = r.data
    return json.loads(data)


def get_all_entites():
    response = make_http_request("GET", DT_GET_ALL_ENTITIES_URL, headers)
    return(response)

def extract_entity_id_from_all(entity_arr):
    entity_id_arr = []
    for entity in entity_arr: 
        entity_id_arr.append(entity["entityId"])
    return entity_id_arr
        

def get_each_entity(entity_id):
    url = DT_GET_EACH_ENTITY_URL + entity_id
    return make_http_request("GET", url, headers)

def get_metrics_memory():
    return make_http_request("GET",DT_GET_METRICS_MEMORY_URL, headers)

def get_metrics_cpu():
    return make_http_request("GET",DT_GET_METRICS_CPU_URL, headers)


def get_p90_memory_by_host_id(memory_arr):
    p90_memory_map = {}
    #TODO: make sure result isn't empty
    data = memory_arr["result"][0]["data"]
    for host_data in data:
        host_name = host_data["dimensions"][0]
        values = host_data["values"]
        values = [x for x in values if x is not None]
        p90 = 0
        if len(values) < 2:
            p90 = values[0]
        else:
            p90 = quantiles(values, n=100)[89]
            p90_memory_map[host_name] = round(p90,2)
    return p90_memory_map

def get_p90_cpu_by_host_id(cpu_arr):
    p90_cpu_map = {}
    #TODO: make sure result isn't empty
    data = cpu_arr["result"][0]["data"]
    for host_data in data:
        host_name = host_data["dimensions"][0]
        values = host_data["values"]
        values = [x for x in values if x is not None]
        p90 = 0
        if len(values) < 2:
            p90 = values[0]
        else:
            p90 = quantiles(values, n=100)[89]
            p90_cpu_map[host_name] = round(p90,2)
    return p90_cpu_map


#TODO: handle next page key on all requests
def gather_dyantrace_data():
    
    get_all_entites_response = get_all_entites()
    entity_id_arr = extract_entity_id_from_all(get_all_entites_response["entities"])
    #print(entity_id_arr)

    entity_arr = []
    for entity_id in entity_id_arr:
        entity_arr.append(get_each_entity(entity_id))
    
    #print(entity_arr)
    
    
    memory_metrics = get_metrics_memory()
    memory_p90_map = get_p90_memory_by_host_id(memory_metrics)
    cpu_metrics = get_metrics_cpu()
    cpu_p90_map = get_p90_cpu_by_host_id(cpu_metrics)

    csv = format_dynatrace_data(entity_arr, memory_p90_map, cpu_p90_map)
    csv_string = format_csv_to_string(csv)
    format_csv_to_string_encode(csv)
    return csv_string
    


def format_dynatrace_data(entity_arr, memory_p90_map, cpu_p90_map):
    server_names = {}
    csv = []
    master_ip_list = []
    csv.append(csv_headers)
    for entity in entity_arr:
        entity_id = entity['entityId']
        properties = entity['properties']
        if 'detectedName' not in properties:
            server_name = random.randint(1, 10000)
        elif properties['detectedName'] in server_names.keys():
            server_name = properties['detectedName'] + random.randint(1, 1000)
        else:
            server_name = properties['detectedName']

        #TODO: reformat for more than one value
        #TODO: whats up with 10.129.0.2
        ip_addresses = properties['ipAddress']
        for address in ip_addresses:
            if address in master_ip_list:
                ip_addresses.remove(address)
            else:
                master_ip_list.append(address)
        ip_addresses_format = ";".join(str(x) for x in ip_addresses)
        cores = 0
        if 'cpuCores' in properties:
            cores = properties['cpuCores']
        elif 'logicalCpuCores' in properties:
            cores = properties['logicalCpuCores']
        memory = 0
        if 'memoryTotal' in properties:
            memory = round(properties['memoryTotal']/1000000)
        #TODO:reformat
        os_name = "N/A"
        if 'osVersion' in properties:
            os_name = properties['osVersion']
            os_name = os_name.replace(",", " ")

        os_architecture = "N/A"
        if 'bitness' in properties:
            os_architecture = "x" + properties['bitness']
        max_cpu = 0
        if entity_id in cpu_p90_map.keys():
            max_cpu = cpu_p90_map[entity_id]
        max_memory = 0
        if entity_id in memory_p90_map.keys():
            max_memory = memory_p90_map[entity['entityId']]

        row = [server_name,ip_addresses_format,cores,memory,os_name,os_architecture,max_cpu,max_memory]
        csv.append(row)
    #print(csv)
    return csv

def format_csv_to_string(csv):
    csv_string = ""
    for row in csv:
        row_string = ",".join(str(x) for x in row) + "\n"
        csv_string = csv_string + row_string


    f = open("dyna_output.csv", "w")
    f.write(csv_string)
    f.close()
    return csv_string

def format_csv_to_string_encode(csv):
    csv_string = ""
    for row in csv:
        row_string = ",".join(str(x) for x in row) + "\n"
        csv_string = csv_string + row_string

    encoded = csv_string.encode('utf-8')


    f = open("dyna_output_encode.csv", "wb")
    f.write(encoded)
    f.close()
    return csv_string

