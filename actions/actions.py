import logging
from typing import Dict, Text, Any, List
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher, Action
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import AllSlotsReset, SlotSet, EventType, ActiveLoop
#from actions.snow import SnowAPI
import random

import datetime as dt 
#from typing import Any, Text, Dict, List

#from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


import json
import requests
#from dotenv import load_dotenv
from pathlib import Path
import os 
from ruamel.yaml import YAML

#logger = logging.getLogger(__name__)
#vers = "vers: 0.1.0, date: Apr 2, 2020"
#logger.debug(vers)


here = Path(__file__).parent.absolute()

yaml=YAML(typ='safe')   # default, if not specfied, is 'rt' (round-trip)
doc = open(f"{here}/env.yml", "r")
fresh_config = yaml.load(doc) or {}   

BASE_URL= fresh_config['base_url']
ALL_TICKETS_URL = BASE_URL + 'tickets'
API_KEY= fresh_config['api_key']

#-------------------------------------------------------------------------------------------------------------------------------------------------
def show_all():
   response = requests.get(ALL_TICKETS_URL,auth=(API_KEY, 'X'))
   return response.json()

class ActionAllTickets(Action):

    def name(self) -> Text:
        return "action_view_tickets"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        data=show_all()
        length=len(data)
        dispatcher.utter_message(text=f"There are {length} messages total. \n")
        for i in range(length):
            message=str((i+1))+ '.'+'\n' + 'id:'+ str(data[i]['id']) + '\n'+ 'subject: '+ data[i]['subject']+'\n'+'Created Date: '+data[i]['created_at']    
            dispatcher.utter_message(text=f"{message}")

        return []
#--------------------------------------------------------------------------------------------------------------------------------------------------------------

def delete_tickets(ids, all_tickets_url= ALL_TICKETS_URL):
    """api call for bulk deleting tickets in freshdesk"""

    headers = { 'Content-Type': 'application/json'}
    
    ticket_ids_url= all_tickets_url +'/'+ 'bulk_delete'

    data = { "bulk_action": {"ids":ids}}
    
    json_data=json.dumps(data);
    
    response = requests.post(ticket_ids_url, headers=headers, data=json_data, auth=(API_KEY, 'X'))
   # print( json_data) 
    return response.status_code, response.json()


class ActionDeleteTickets(Action):

    def name(self) -> Text:
        return "action_inform_delete_ids"

    def run(self, dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        """action for deleting ticket(s) in freshdesk"""

        ids =tracker.get_slot("ids")
         
        #http_status, content= delete_tickets(ids, ALL_TICKETS_URL)
        #dispatcher.utter_message(text= f"ids: {ids}\n status: {http_status}")

        if not ids:
            dispatcher.utter_message(response = "utter_ask_ids")
            return []

        else:

            ids= [ int(_) for _ in ids]
            http_status, content= delete_tickets(ids, ALL_TICKETS_URL)

            if(http_status ==202):
                dispatcher.utter_message(text=f"Find details for the deletion job for ticket ids {ids}.")
                dispatcher.utter_message(text=f"{content}")
                return [SlotSet("ids", None)]
            else:
                dispatcher.utter_message(f'{http_status}: Something is wrong')   
                

#---------------------------------------------------------------------------------------------------------------------------------------------------------
def view_id(id, all_tickets_url):
    """api call for viewing a ticket in freshdesk"""
    
    headers = { 'Content-Type': 'application/json'}
    
    id_url= all_tickets_url + '/'+ str(id)

    response = requests.get(id_url, headers=headers, auth=(API_KEY, 'X'))

    return response.status_code, response.json()


class ActionViewId(Action):

    def name(self) -> Text:
        return "action_inform_view_id"

    def run(self, dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        """action for viewing ticket in freshdesk"""

        id =tracker.get_slot("id")
       
        if not id:
            dispatcher.utter_message(response = "utter_ask_id")
            return []

        else:
            http_status, content= view_id(id, ALL_TICKETS_URL)

            if(http_status ==200):
                dispatcher.utter_message(text=f"Here are the details for ticket {id}.")
                dispatcher.utter_message(text=f"{content}")
                return [SlotSet("id", None)]
            else:
                dispatcher.utter_message(f'{status}: Something is wrong')   
        
    
#---------------------------------------------------------------------------------------------------------------------------------------------------------
def create_ticket(description,subject,email,priority,status):
    """api call for create aticket in freshdesk help desk"""
    
    headers = { 'Content-Type': 'application/json'}
    
    data = { "description": description, "subject": subject, "email": email, "priority": priority, "status": status} 
    
    json_data=json.dumps(data);

    response = requests.post(ALL_TICKETS_URL, headers=headers, data=json_data, auth=(API_KEY, 'X'))

    return response.status_code, response.json()

class ActionTicketCreated(Action):

    def name(self) -> Text:
        return "action_ticket_created"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        """action for create ticket in freshdesk"""

        description = tracker.get_slot("description")
        subject= tracker.get_slot("subject")  
        email = tracker.get_slot("email")
        priority_code =  int(tracker.get_slot("priority"))
        status_code = int(tracker.get_slot("status"))
        
      
        http_status, content = create_ticket(description,subject,email,priority_code,status_code)

       # dispatcher.utter_message(f'description: {description}, subject: {subject}, email: {email}, priority:{ priority_code}, status: {status_code}')
        dispatcher.utter_message(text = f'The new ticket is sucessfully created in freshdesk. Here are the Details')
        dispatcher.utter_message( text = f'http_status: {http_status} \n content: {content}')
        #dispatcher.utter_message(f'{http_status}')
        #if(http_status==201):
        #    
        #else:
        #    dispatcher.utter_message(f'Something bad happend while ticket creation')
       
        return [AllSlotsReset()]

#---------------------------------------------------------------------------------------------------------------------------------------------------

def update_ticket(ticket_id,priority,status):
    """api call for update a ticket in freshdesk"""

    headers = { 'Content-Type': 'application/json'}

    ticket_id_url= ALL_TICKETS_URL +'/'+ str(ticket_id)

    data = { "priority": priority, "status": status }
    
    json_data=json.dumps(data);
    
    response = requests.put(ticket_id_url, headers=headers, data=json_data, auth=(API_KEY, 'X'))
    
    return response.status_code, response.json()

class ActionTicketUpdated(Action):

    def name(self) -> Text:
        return "action_ticket_updated"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        """action for update ticket in freshdesk"""

        ticket_id = tracker.get_slot("1_ticket_id")
        priority_up_code = int(tracker.get_slot("3_priority_up"))
        status_up_code = int(tracker.get_slot("2_status_up"))
        
        http_status, content = update_ticket(ticket_id, priority_up_code, status_up_code)

        if(http_status == 200):
            dispatcher.utter_message(f'The ticket {ticket_id} is sucessfully updated in freshdesk')
        else:
            dispatcher.utter_message('Something bad happend while ticket updation')          
            
        return [AllSlotsReset()]




#---------------------------------------------------------------------------------------------------------------------------------------------------


class ActionShowTime(Action):

    def name(self) -> Text:
        return "action_show_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text=f"{dt.datetime.now()}")

        return []
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
