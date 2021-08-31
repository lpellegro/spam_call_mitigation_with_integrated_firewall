# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import requests
from requests.auth import HTTPBasicAuth

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
       data = {"Priority": priority, "Address": ip, "EndPort": 5061, "Interface": "LAN2", "Action": "Reject", "PrefixLength": 32, "Service": "Custom", "StartPort": 5060, "Transport": "TCP"}
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
       return
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


