from ._anvil_designer import StandingsTemplate
from anvil import *
import stripe.checkout
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import data_access

class Standings(StandingsTemplate):
  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.sort_by('Total', False)
    self.button_1.align = "full"
    self.button_2.align = "full"
    self.button_3.align = "full"
    self.button_4.align = "full"
    self.button_5.align = "full"
    self.button_6.align = "full"
    self.button_7.align = "full"
    self.button_8.align = "full"
    self.button_9.align = "full"
    # Any code you write here will run when the form opens.

  def button_1_click(self, **event_args):
    self.sort_by('Teamnum', True)
    
  def button_2_click(self, **event_args):
    self.sort_by('Teamname', True)
    
  def button_3_click(self, **event_args):
    self.sort_by('April', False)
    
  def button_4_click(self, **event_args):
    self.sort_by('May', False)
    
  def button_5_click(self, **event_args):
    self.sort_by('June', False)
    
  def button_6_click(self, **event_args):
    self.sort_by('July', False)
    
  def button_7_click(self, **event_args):
    self.sort_by('August', False)
    
  def button_8_click(self, **event_args):
    self.sort_by('September', False)
    
  def button_9_click(self, **event_args):
    self.sort_by('Total', False)
    
 
    
  def sort_by(self,colname, asc):
    self.repeating_panel_standings.items = anvil.server.call('standings',colname, asc)
    self.refresh_data_bindings()

  

