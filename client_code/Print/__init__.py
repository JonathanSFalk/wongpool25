from ._anvil_designer import PrintTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from ..TeamColumn import TeamColumn

from anvil.tables import app_tables

class Print(PrintTemplate):
  def __init__(self, my_teams, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.my_teams = my_teams
    tlist = []     
    for t in self.my_teams:
        tlist.append(TeamColumn(teamrow=t,print_switch=True))
    box=FlowPanel(width=800)
    for c in tlist:
        box.add_component(c)
    self.content_panel.add_component(box)
