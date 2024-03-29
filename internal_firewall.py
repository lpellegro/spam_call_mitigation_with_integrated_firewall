# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import requests
from requests.auth import HTTPBasicAuth
from credentials import credentials

def ip_port_info(expe, peer):
    expe_list = expe.split(':')

    expe_ip = expe_list[0]
    if peer == '127.0.0.1':
        peer = expe_ip

    if len(expe_list) == 1:  # use of standard port for https (443)
        peer_with_port = peer

    if len(expe_list) > 1:
        peer_with_port = peer + ':' + expe_list[1]
    return expe_ip, peer, peer_with_port

#set the firewall rules
def missing_elements (list):
    if list == []:
       return []
    else:
       start, end = list[0], list[-1]
       return sorted(set(range(start, end + 1)).difference(list))

def firewall(ip, action, expe, username, secret):
    #get the firewall rules
    ip_list = []
    url = 'https://' + expe + '/api/provisioning/common/firewallrules/configuration'
    try:
        print ('sending request to: ', url)
        response = requests.get(url, auth=HTTPBasicAuth(username, secret))
        status = response.status_code
        if str(status).startswith('2'):
           ip_list = response.json()
           print('Lenght of answer is: ', len(ip_list))
        if len(ip_list) == 0:
           print("JSON empty answer")
    except requests.exceptions.HTTPError:
        print('Connection error')
        #return new_items
    priority_list = []
    n_rules = len(ip_list)
    index = ''
    failure = False

    if len(ip_list) == 0:
      priority = 1
    else:
      for n in range(n_rules):
          if ip_list[n]['Address'] == ip:
             index = ip_list[n]['Index']
             current_priority = ip_list[n]['Priority']
             priority_list.append(current_priority)
             break
          current_priority = ip_list[n]['Priority']
          priority_list.append(current_priority)

      priority_list.sort()
      print('priority_list is: ', priority_list)
      gaps = missing_elements(priority_list)
      print(gaps)
      if gaps != []:
          priority = gaps[0]
      else:
          priority = priority_list[-1] + 1

    if action == 'ban' and index != '':
       print ('Already banned')
       return

    if action == 'ban' and index == '':
       print ('Creating an entry in the firewall')
       expe_fqdn, peer, peer_with_port = ip_port_info (expe, expe)
       dual_nic_support = credentials[expe_fqdn][2]
       if dual_nic_support == True:
          LAN = "LAN2"
       else:
          LAN = "LAN1"
       data = {"Priority": priority, "Address": ip, "EndPort": 5061, "Interface": LAN, "Action": "Deny", "PrefixLength": 32, "Service": "Custom", "StartPort": 5060, "Transport": "TCP", "Description": "Script generated - spam calls"}
       try:
          response = requests.post(url, json=data, auth=HTTPBasicAuth(username, secret))
          print(response)
          print(response.json())

       except:
          failure = True
          error = True
          pass

    if action == 'unban' and index == '':
       print ('already unbanned')
       return error
    if action == 'unban' and index != '':
       print(index)
       data = {"Index": index}
       try:
           response = requests.delete(url, json=data, auth=HTTPBasicAuth(username, secret))
           print(response)
           print(response.json())

       except:
           failure = True
           error = True
           pass

    if failure == False:
       message = response.json()['Message']
       if 'activate' or 'uccess' in message:
           error = False
       else:
           error = True
       print ('error is: ', error)

    if error == False:
       try:
           activate_url = 'https://' + expe + '/api/provisioning/common/firewallrules/activation'
           response = requests.put(activate_url, auth=HTTPBasicAuth(username, secret))

       except:
           failure = True
           error = True
           pass
       activation_message = response.json()['Message']
       if 'uccess' in activation_message:
           error = False
    return error


