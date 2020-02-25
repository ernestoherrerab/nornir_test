from nornir import InitNornir
from nornir.core.filter import F
from nornir.plugins.functions.text import print_result , print_title
from nornir.plugins.tasks.networking import netmiko_send_config , netmiko_send_command, netmiko_save_config
import ntc_templates
import time
from pprint import pprint

def main():
    start = time.time()
    nr = InitNornir (config_file='config/config.yml', dry_run=True,logging={"file": "logfile","level": "debug"})
    #nrdict = nr.dict()
    '''
    #print (type(nrdict))
    #for key, value in nrdict.items():
     #   print (key, value)
    '''
    if  nr.filter(F(groups__contains='nexus')):
        nexus = nr.filter(F(groups__contains='nexus'))
        print (nexus.inventory.hosts.keys())
        result = nexus.run(task=get_facts_nxos)
    if  nr.filter(~F(groups__contains='nexus')):
        ios = nr.filter(~F(groups__contains='nexus'))
        iosdict = ios.dict()
        pprint (iosdict['inventory']['hosts'])
        print (ios.inventory.hosts.items())
        result2 = ios.run(task=get_facts)
        
   
    end = time.time()
    elapssed = end - start
    tt = str(elapssed)
    print ("ELAPSED "+ tt)

def get_facts(task):
   
    r = task.run( netmiko_send_command,  command_string="show cdp neighbors detail", use_textfsm=True)
    task.host["facts"] = r.result
      
   
    for i in task.host["facts"]:
        remote_port =  (i['remote_port'])
        local_port = (i['local_port'])
        destination_host = (i['destination_host'])
        set_commands = ['interface ' + local_port,'description '+ destination_host +'@' + remote_port]
        print (set_commands)
        c = task.run (netmiko_send_config, config_commands = set_commands )
        print_result (c)
    s = task.run (netmiko_save_config)
    print_result (s)
    

def get_facts_nxos(task):
   
    r = task.run( netmiko_send_command,  command_string="show cdp neighbors detail", use_textfsm=True)
    task.host["facts"] = r.result
   
    print ('NEXUSSSSSSSSSSSSSS!!!!!!!!!!!!!!!!')
    #print (task.host["facts"]) 
    
    for i in task.host["facts"]:
        remote_port =  (i['remote_port'])
        local_port = (i['local_port'])
        destination_host = (i['dest_host'])
        set_commands = ['interface ' + local_port,'description '+ destination_host +'@' + remote_port]
        print (set_commands)
        c = task.run (netmiko_send_config, config_commands = set_commands )
        print_result (c)
    s = task.run (netmiko_save_config)
    print_result (s)
    
        
        






if __name__ == '__main__':
    main()

  