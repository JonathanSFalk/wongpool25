from ._anvil_designer import PlayersTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Players(PlayersTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.repeating_panel_1.items = anvil.server.call('players','plast',True)
    self.button_2.align = "full"
    self.button_2.width = "17em"
    # Any code you write here will run when the form opens.

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.sort_by('pnum', True)

  def button_2_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.sort_by('plast', True)

  def button_3_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.sort_by('April', False)

  def button_4_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.sort_by('May', False)

  def button_5_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.sort_by('June', False)

  def button_6_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.sort_by('July', False)

  def button_7_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.sort_by('August', False)

  def button_8_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.sort_by('September', False)
  
  def button_9_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.sort_by('Total', False)
   
  def sort_by(self,colname, asc):
    self.repeating_panel_1.items = anvil.server.call('players',colname, asc)
    self.refresh_data_bindings()










