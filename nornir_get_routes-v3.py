from nornir import InitNornir
from nornir.core.filter import F
from nornir.plugins.functions.text import print_result , print_title
from nornir.plugins.tasks.networking import netmiko_send_config , netmiko_send_command, netmiko_save_config
#import ntc_templates
import time
from pprint import pprint
from nornir.core.deserializer.inventory import InventoryElement
import json
import os


def create_dir(dir_to_create):
    if not os.path.exists(dir_to_create):
                   os.mkdir(dir_to_create) 
                   print ("Directory",dir_to_create,"created")


def main():
    create_dir('outputs')
    '''
    THIS IS FOR KNOWING FOR WHERE IS LOADING THE MODULE
    #print (ntc_templates.__file__)
    '''
    
    start = time.time()
    nr = InitNornir (config_file='config/config.yml', dry_run=True,logging={"file": "logfile","level": "debug"})
    #nrdict = nr.dict()
    global total
    total =  (len(nr.inventory.hosts))
    '''
    #print (type(nrdict))
    #for key, value in nrdict.items():
     #   print (key, value)
    '''
    

    if  nr.filter(F(groups__contains='nexus')):
        nexus = nr.filter(F(groups__contains='nexus'))
        #print (nexus.inventory.hosts.keys())
        result = nexus.run(task=get_facts_nxos)
    if  nr.filter(~F(groups__contains='nexus')):
        ios = nr.filter(~F(groups__contains='nexus'))
        iosdict = ios.dict()
        #pprint (iosdict['inventory']['hosts'])
        #print (ios.inventory.hosts.items())
        result2 = ios.run(task=get_facts)
        
        
   
    end = time.time()
    elapssed = end - start
    tt = str(elapssed)
    print ("ELAPSED "+ tt)
    

def get_facts(task):

    comm = 'show cdp neighbors detail'
    x = task.run( netmiko_send_command,  command_string=comm, use_textfsm=True)

    neigh = x.result
    host = task.host.hostname
    newdir = f'outputs/{host}'
    create_dir(newdir)
    dump_interfaces(comm,neigh,host,newdir)



    comm = 'show ip interface brief'
    y = task.run( netmiko_send_command,  command_string=comm, use_textfsm=True)
    
    parsed_ints =  y.result
    host = task.host.hostname
    newdir = f'outputs/{host}'
    create_dir(newdir)
    clean_interfaces(parsed_ints)
    while {} in parsed_ints:
            parsed_ints.remove({})
    dump_interfaces(comm,parsed_ints,host,newdir)

    r = task.run( netmiko_send_command,  command_string="show vrf", use_textfsm=True)
    task.host["facts"] = r.result
   


    #print (task.host.hostname)
   
    
       
    if isinstance (task.host["facts"], str):
            
            comm = 'show ip route'
            s = task.run (netmiko_send_command, command_string = comm, use_textfsm=True)
            task.host["facts"] = s.result
            #print (task.host.hostname)
            host = task.host.hostname
            #print (f'{host} {comm} ESTE NO TIENE VRFS')
            
            vrf_name = 'default'
            #print (comm)
            #print (task.host["facts"])  
            parsed = task.host["facts"]
            clean_routes(parsed)
            
            dump_command(comm,parsed,host,newdir,vrf_name) 
    else:



            for i in task.host["facts"]:
                vrf_name =  (i['name'])
                comm = f'show ip route vrf {vrf_name}'
                #print (comm)
                #print (task.host.hostname)
                host = task.host.hostname
                newdir = f'outputs/{host}'
                create_dir(newdir)
                #print (comm)
                s = task.run (netmiko_send_command, command_string = comm, use_textfsm=True)
                task.host["facts"] = s.result
                parsed = task.host["facts"]
                clean_routes(parsed)
                dump_command(comm,parsed,host,newdir,vrf_name)   
            comm = 'show ip route'
            #print (comm)
            s = task.run (netmiko_send_command, command_string = comm, use_textfsm=True)
            task.host["facts"] = s.result
            vrf_name = 'default'
            #print (task.host.hostname)
            host = task.host.hostname
            #print (comm)
            #print (task.host["facts"])  
            parsed = task.host["facts"]
            dump_command(comm,parsed,host,newdir,vrf_name) 
def clean_interfaces(parsed):
    
    for i in (parsed):
        if i['ipaddr']=='unassigned':
                #print (parsed[i])
                #del parsed[i]
                i.pop('ipaddr')
                i.pop('intf')
                i.pop('status')
                i.pop('proto')
               
                #print(type(i))
    

def clean_routes(parsed):
    
    for i in parsed:
                  nhip = i.pop('nexthop_ip')
                  nhif = i.pop('nexthop_if')
                  i.pop('uptime')
                  subnet = i['network'] +'/'+ i['mask']
                  i['subnet']= subnet
                  i['nexthop'] = nhip
                  i['interface'] = nhif
                  typ = i.pop('type')
                  distance = i.pop('distance')
                  metric = i.pop('metric')
                  i.pop('network')
                  i.pop('mask')
                  if i['protocol'] == 'B':
                      i.pop('protocol')
                      i['protocol'] = 'BGP'
                  if i['protocol'] == 'O':
                      i.pop('protocol')
                      i['protocol'] = 'OSPF'
                  if i['protocol'] == 'S':
                      i.pop('protocol')
                      i['protocol'] = 'STATIC'
                  if i['protocol'] == 'C':
                      i.pop('protocol')
                      i['protocol'] = 'CONNECTED'
                  if i['protocol'] == 'D':
                      i.pop('protocol')
                      i['protocol'] = 'EIGRP'
                  if i['protocol'] == 'L':
                      i.pop('protocol')
                      i['protocol'] = 'LOCAL'
                  i['type'] = typ
                  i['distance'] = distance
                  i['metric'] = metric
                  

def get_facts_nxos(task):
   
    r = task.run( netmiko_send_command,  command_string="show vrf", use_textfsm=True)
    task.host["facts"] = r.result
   
def dump_interfaces (command,command_parsed,host,newdir):
       command = command.replace(' ','_')
       filename = command +'.json'
           
       filename = '/'.join((newdir, filename))
       END_DICT = { command : command_parsed }
       with open(filename,'w') as f:
               json.dump(END_DICT,f, indent = 2)   
def dump_command(command,command_parsed,host,newdir,vrf_name):
       
       filename = command.replace(' ','_')+'.json'
       
       filename = '/'.join((newdir, filename))
       END_DICT = { vrf_name : command_parsed }
       with open(filename,'w') as f:
               json.dump(END_DICT,f, indent = 2)   
        
        






if __name__ == '__main__':
    main()

  