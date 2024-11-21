#!/usr/bin/env python3 

import datetime 
import os
import sys
from kubernetes import client, config
from kubernetes.client import configuration

now = datetime.datetime.now()
curtime = now.strftime('%Y-%m-%d-%H-%M-%S')

# A Directory for saving data
DATA_DIR = os.getcwd() + "/data/"

# Kube context names
CLUSTERS = [
    "minikube",
]

SYMBOLS = {
    'customary'     : ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'),
    'customary_ext' : ('byte', 'kilo', 'mega', 'giga', 'tera', 'peta', 'exa', 'zetta', 'iotta'),
    'iec'           : ('Bi', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'),
    'iec_ext'       : ('byte', 'kibi', 'mebi', 'gibi', 'tebi', 'pebi', 'exbi', 'zebi', 'yobi'),
}

def process_cluster(filename, cluster):
    contexts, active_context = config.list_kube_config_contexts()
    if not contexts:
        print("Cannot find any context in kube-config file.")
        return False

    f = open(filename, "w")
    
    try:
        api = client.CustomObjectsApi(api_client=config.new_client_from_config(context=cluster))
        v1 = client.CoreV1Api(api_client=config.new_client_from_config(context=cluster))
    except Exception as e:
        print(f'Error: {e}')
        sys.exit()
    
    k8s_pods_stats = api.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "pods")
    k8s_pods_data = v1.list_pod_for_all_namespaces(watch=False)

    pods_data = {}

    for pod in k8s_pods_data.items:
        pod_name = pod.metadata.name
        pod_containers = []
        for container in pod.spec.containers:
            if container.resources.requests:
                try:
                    cpu = container.resources.requests['cpu']
                    memory = container.resources.requests['memory']
                except:
                    cpu = None
                    memory = None
            else: 
                cpu = None
                memory = None
            pod_containers.append({ 'name': container.name, 'cpu': cpu, 'memory': memory })
        
        pods_data[pod_name] = { 'namespace': pod.metadata.namespace, 'containers': pod_containers }
    
    f.write(f'Pod,Container,Namespace,CPU Req,CPU Usage,CPU Idle, Memory Req, Memory Usage, Memory Idle\n')
    for stats in k8s_pods_stats['items']:
        data = stats["metadata"]
        pod_name = data['name']
        if pod_name in pods_data.keys(): 
            for container in stats['containers']:
                cont_name = container['name']
                cpu = None
                memory = None
                for cont in  pods_data[pod_name]['containers']:
                    if cont['name'] == cont_name:
                        cpu = cont['cpu']
                        memory = cont['memory']

                if cpu != None:
                    cpu_req = norm_cores(cpu)
                else:
                    cpu_req = cpu

                try:
                    mem_req = human2bytes(memory)
                except:
                    mem_req = None

                if container["usage"]["cpu"] != None:
                    cpu_fact = norm_cores(container["usage"]["cpu"])

                try:
                    mem_fact = human2bytes(container["usage"]["memory"])
                except:
                    mem_fact = None

                if cpu != None:
                    try:
                        cpu_idle = round((100 - (cpu_fact / (cpu_req / 100))), 0)
                        if cpu_idle < 0:
                            cpu_idle = 0
                    except:
                        cpu_idle = None
                else:
                    cpu_idle = None

                if memory != None:
                    try:
                        mem_idle = round((100 - (mem_fact / (mem_req / 100))), 0)
                        if mem_idle < 0:
                            mem_idle = 0
                    except:
                        mem_idle = None
                else:
                    mem_idle = None
            
                f.write(f'{data['name']},{container["name"]},{data["namespace"]},cpu_requested: {cpu_req},cpu_used: {cpu_fact},cpu_idle: {cpu_idle},memory_requested: {mem_req},memory_used: {mem_fact}, mem_idle: {mem_idle}\n')
    f.close()

def makedir(directory_name):
    try:
        os.mkdir(directory_name)
        print(f"Directory '{directory_name}' created successfully.")
        return True
    except FileExistsError:
        print(f"Directory '{directory_name}' already exists.")
        return True
    except PermissionError:
        print(f"Permission denied: Unable to create '{directory_name}'.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def main():
    print("Making main directory")
    try:
        makedir(DATA_DIR)
    except:
        print("Main directory creation failed")
        sys.exit(2)

    for context in CLUSTERS:
        cluster_dir = DATA_DIR + context + "/"
        
        try: 
            makedir(cluster_dir)
        except:
            print("Main directory creation failed")
            sys.exit(2)
        
        filename = cluster_dir + context + "-" + curtime + ".log"
        process_cluster(filename,context)

def bytes2human(n, format='%(value).1f %(symbol)s', symbols='customary'):
    n = int(n)
    if n < 0:
        raise ValueError("n < 0")
    symbols = SYMBOLS[symbols]
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i+1)*10
    for symbol in reversed(symbols[1:]):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            return format % locals()
    return format % dict(symbol=symbols[0], value=n)

def human2bytes(s):
    init = s
    num = ""
    while s and s[0:1].isdigit() or s[0:1] == '.':
        num += s[0]
        s = s[1:]
    num = float(num)
    letter = s.strip()
    for name, sset in SYMBOLS.items():
        if letter in sset:
            break
    else:
        if letter == 'k':
            sset = SYMBOLS['customary']
            letter = letter.upper()
        else:
            raise ValueError("can't interpret %r" % init)
    prefix = {sset[0]:1}
    for i, s in enumerate(sset[1:]):
        prefix[s] = 1 << (i+1)*10
    return int(num * prefix[letter])


def norm_cores(s):
    if s[-1] == 'm':
        cpu_req = s[:-1]
        return float(cpu_req) / 1000
    elif s[-1] == 'n':
        cpu_req = s[:-1]
        return round(float(cpu_req) / 1000000000, 4)
    elif s[-1] == 'u':
        cpu_req = s[:-1]
        return round(float(cpu_req) * 0.000001, 4)
    else:
        return float(s)

if __name__ == "__main__":
    main()
