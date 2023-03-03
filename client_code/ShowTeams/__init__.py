from ._anvil_designer import ShowTeamsTemplate
from anvil import *
import anvil.facebook.auth
import stripe.checkout
import anvil.media
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..TeamColumn import TeamColumn

class ShowTeams(ShowTeamsTemplate):
  def __init__(self, my_teams, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.my_teams = my_teams
    tlist = []     
    for t in self.my_teams:
        tlist.append(TeamColumn(teamrow=t,print_switch=False))
    box=FlowPanel(width=800)
    for c in tlist:
        box.add_component(c)
    self.content_panel.add_component(box)
    

    

  def button_1_click(self, **event_args):
    open_form('TeamPicker')

  def button_2_click(self, **event_args):
    pdf = anvil.server.call('create_pdf', self.my_teams)
    anvil.media.download(pdf)


