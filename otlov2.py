# _*_ coding:utf-8 _*_
#!/usr/bin/python
from pysnmp.hlapi import *
import subprocess
import pdb
import sys
import pprint
# behind for canfe track
import requests
from requests.auth import HTTPDigestAuth
from requests.auth import HTTPBasicAuth 
import time
from BeautifulSoup import BeautifulSoup 
import re 
import random

IP = raw_input("sw ip : ") 
VLAN = raw_input("vlan : ")
ticket_number =  raw_input("ticket number : ") 
counter = raw_input("how many times check? (6 houers) : ")
counter = int(counter)
if_desc_oid = "1.3.6.1.2.1.2.2.1.2"

class snmp:
   def get_snmp_next(self,ip,oid):   # return dict with { OID : RESPONSE }
      find = {}
      for (errorIndication,
           errorStatus,
           errorIndex,
           varBinds) in nextCmd(SnmpEngine(),
                 CommunityData('community'),
                 UdpTransportTarget((ip, 161), timeout=5.0, retries=2),
                 ContextData(),
                 ObjectType(ObjectIdentity(oid)),
                 lookupMib=False, lexicographicMode=False):

         if errorIndication:
            print(errorIndication)
            break
         elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                   errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
         else:
            for varBind in varBinds:
                var = [x.prettyPrint() for x in varBind]
                find.update({ var[0]:var[1] })
      return find 
   def snmp_get_desc(self,ip):
     g =  getCmd(SnmpEngine(),
             CommunityData('community'),
             UdpTransportTarget((ip, 161)),
             ContextData(),
             ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))
     errorIndication, errorStatus, errorIndex, varBinds = next(g)
     if errorIndication:
        print(errorIndication)
        sys.exit() 
     elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
               errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        sys.exit()
     else:
        try:
            Desc = str(varBinds[0].prettyPrint())
        except:
            sys.exit("blyad' .\n 4to za huiniya? \n Vozmozhno chtoto so swithem.")
     return Desc
class snmp_edithor:
   def get_decimilar_mac(self, oid_response):
           mac_list = []
           for oid in oid_response:
              val = oid.split(".")[-6:]
              mac_list.append(".".join(val))
           return mac_list
   def get_vlan_port_in_fox(self,oid_response,vlan ):
           vlan_port_list = []
           for oid in oid_response:
              port  = oid.split(".")[-1]
              vlan_port_list.append(port) if oid_response.get(oid) == vlan else ""
           return vlan_port_list
   def get_vlan_port_in_icome(self,oid_response,vlan ):
           trunk_port = {ports:oid for oid , ports in oid_response.items() if oid.split(".")[-7] == "1000"}.keys()
           oid_response = {oid:port  for oid, port in oid_response.items() if oid.split(".")[-7] == vlan }
           oid_dict =  oid_response.items()
           vlan_port = { port : [oid.split(".")[-6:] for oid in oid_response if oid_response[oid]  == port] for oid, port in oid_dict }
           for ports in trunk_port:
              vlan_port.pop(ports, None)
           return vlan_port 
   def get_port_mac(self, oid_response):
      port_mac_list = oid_response.items()
      value = {port_mac[0]:
         [[hex(int(num)).replace("0x","")  for num in macs]
              for macs in port_mac[1] ]
                 for port_mac in port_mac_list}
      return value
class define_switch:
   def __init__(self, snmp, text, ip, vlan):
      self.snmp = snmp
      self.desc_string = snmp.snmp_get_desc(ip)
      self.text = text
#      self.data = snmp()
      self.VLAN = vlan
      self.IP = ip
   def swtch_model(self,):                  # return dict {port : list of mac in hex }
      print self.desc_string                # mac divided on hex numbers ["aa","bb","cc","dd","ee","ff"]
      if "ROS" or "S6324" or "Summit" in self.desc_string :
#         print  "This is Raisecom"
         vlan_port_oid = "1.3.6.1.2.1.17.7.1.2.2.1.2"
#         mac_port_oid = "1.3.6.1.2.1.17.7.1.2.2.1.2"
         com_mac = self.snmp.get_snmp_next( self.IP, vlan_port_oid )
         mac_port = self.text.get_vlan_port_in_icome(com_mac,self.VLAN)
         port_mac = self.text.get_port_mac(mac_port)
         print port_mac
         return port_mac
class send_to_trac:
   def __init__(self, ticket_number,comment ):
      self.URL = "http://trac.com/ticket/" + ticket_number
      self.comment = comment
   def payload2(self, hed,text,summary ):
      payload={\
         "__FORM_TOKEN" : hed,\
         "__EDITOR__1" : "textarea",\
         "comment" : self.comment,\
         "field_summary" : summary,\
         "__EDITOR__2" : "textarea",\
         "field_description" : "",\
         "field_type" : u"info",\
         "field_priority" : "major",\
         "field_milestone" : "",\
         "field_component" : u"Отлов клиентов",\
         "field_keywords" : "",\
         "field_cc" : "",\
         "action" : "leave",\
         "start_time" : str(int(time.time()*1000000)),\
         "view_time" : self.get_viev_time(text),\
         "replyto" : "",\
         "submit" : "Submit+changes"\
          }
      return payload
   def get_viev_time(self, trac_page):
      viev_time_index = trac_page.rfind("name=\"view_time\" value=\"")
      viev_time = trac_page[viev_time_index + 24:viev_time_index + 40]
      return viev_time
   def message(self,):
      with requests.Session() as s:
         s.auth= ('login', 'pass')
         ticket = s.get(self.URL)
         hed = str(ticket.cookies["trac_form_token"])
         html_page = BeautifulSoup(ticket.text)
         summary = html_page.html.body.h1.span.text
         pay = self.payload2(hed,ticket.text,summary)
         print_text =  s.post(URL,  data=pay, cookies=ticket.cookies)

# this code catch abons 
snmp = snmp()
text = snmp_edithor()
define_sw = define_switch(snmp, text, IP, VLAN)
port_mac = define_sw.swtch_model()
# end 
# this code have to compare macs between the cycle
# start monkey code
flag = True
while flag:

   delay  = random.randint(19, 21)
#   delay random.randint(19000, 21600)
   port_mac_2 = define_sw.swtch_model()   
# start comaring
   for i in port_mac_2.keys():
      if port_mac.get(i) == None:
         port_mac.update({i:b.pop(i)})
   for i in  port_mac_2.items():
      upd = []
      iter_logins = port_mac.get(i[0])
      if port_mac.get(i[0]) <> i[1]:
        for b in i[1]:
           if port_mac.get(i[0]).count(b) == 0:
              upd.append(b)
        port_mac.update({i[0]:iter_logins + upd})
   counter = counter -1 
   print counter
   if counter > 0 :
      break 
   sleep(delay)
print port_mac
# end compare
if_desc = snmp.get_snmp_next(IP,if_desc_oid)
port_login = {}
banjo = shell()
for port in port_mac:
   macs = port_mac.get(port)
   logins_in_port = []
   logins_in_port = [ banjo.shell_banjo(":".join(mac)).replace("\n","") for mac in macs ]
   port_login.update({if_desc.get(if_desc_oid + "." + port) : logins_in_port})

print "xxxxxxxxxUSERSxxxxxxxxxxx"
print pprint.pformat(port_login)

# this for sending message
e = send_to_trac(ticket_number, comment)
e.message()
