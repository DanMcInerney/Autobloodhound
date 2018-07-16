#!/usr/bin/env python3

import argparse
import simplejson as json
from IPython import embed
import signal
import msfrpc
from termcolor import colored

def parse_args():
    # Create the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="JSON exported graph data from BloodHound")
    parser.add_argument("-p", "--password", default="123", help="Password for msfrpc")
    parser.add_argument("-u", "--username", default="msf", help="Username for msfrpc")
    parser.add_argument("--debug", action="store_true", help="Debug info")
    return parser.parse_args()

def get_first_node(edges):
    targets = [x['target'] for x in edges]
    sources = [x['source'] for x in edges]
    first_node = set(sources) - set(targets)
    # sets don't allow slicing/indexing
    for x in first_node:
        first_node = x
    return first_node

def parse_json():
    with open(args.file, 'r') as f:
        json_data = f.read()
        parsed_json = json.loads(json_data)
        return parsed_json

def find_attack_path(edges, nodes, first_node):
    attack_path = [first_node]
    attack_path = create_attack_path(attack_path, edges, nodes, first_node)
    return attack_path
    
def create_attack_path(attack_path, edges, nodes, source):
    next_target = None
    label = None

    for i in edges:
        if i['source'] == source['id']:
            next_target = get_node_data(i['target'], nodes)
            label = i['label']
            break

    if next_target:
        print('Adding {} and {} to attack_path'.format(label, str(next_target)))
        attack_path += [label, next_target]
        return create_attack_path(attack_path, edges, nodes, next_target)

    else:
        return attack_path

def get_node_data(obj_id, nodes):
    node_copy = None
    remove = ['glyphs', 'folded', 'x', 'y', 
              'size', 'degree', 'icon', 'fa2_x', 
              'fa2_y', 'dn_x', 'dn_y', 
              'dn_size', 'dn', 'type_computer',
              'type_group', 'type_user']

    for i in nodes:
        if i['id'] == obj_id:
            node_copy = i
            for k in remove:
                if k in node_copy:
                    del node_copy[k]

    return node_copy

def get_attack_path():
    parsed_json = parse_json()
    edges = parsed_json['edges']
    nodes = parsed_json['nodes']
    first_node = get_node_data(get_first_node(edges), nodes)
    attack_path = find_attack_path(edges, nodes, first_node)
    for x in attack_path:
        print(x)

def get_msf_client():
    client = msfrpc.Msfrpc({})
    try:
        client = get_perm_token(client)
    except:
        print_bad('Failed to connect to MSF RPC server,'
                  ' are you sure metasploit is running and you have the right password?',
                  None, None)
        sys.exit()

    return client

def find_starting_sess(sessions):


def main():
    client = get_msf_client()
    attack_path = get_attack_path()
    sessions = client.call('session.list')
    starting_sess = find_starting_sess(sessions)

if __name__ == "__main__":
    args = parse_args()
    main()
