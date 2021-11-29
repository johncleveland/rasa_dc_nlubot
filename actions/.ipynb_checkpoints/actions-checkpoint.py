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


#-------------------------------------------------------------------------------------------------------------------------------------------------

ticket_url =fresh_config['all_ticket_url']
api_key= fresh_config['api_key']

def show_all():
  response = requests.get(ticket_url,auth=(api_key, 'X'))
  return response.json()

class ActionAllTickets(Action):

    def name(self) -> Text:
        return "action_view_tickets"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        data=show_all()
        length=len(data)
        for i in range(length):
            message=str((i+1))+ '.'+'\n' + 'id:'+ str(data[i]['id']) + '\n'+ 'subject: '+ data[i]['subject']+'\n'+'Created Date: '+data[i]['created_at']    
            dispatcher.utter_message(text=f"{message}")

        return []


#---------------------------------------------------------------------------------------------------------------------------------------------------------


class ActionCreateTicket(Action):

    def name(self) -> Text:
        return "action_create_ticket"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text=f"Ticket Created !")

        return []

#---------------------------------------------------------------------------------------------------------------------------------------------------


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_show_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text=f"{dt.datetime.now()}")

        return []
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
