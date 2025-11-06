from ._anvil_designer import PlayersToTeamsTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import data_access

class PlayersToTeams(PlayersToTeamsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    retmat = data_access.get_p2team()
    retmat = anvil.server.call('p2team')
    # Any code you write here will run when the form opens.
    for r in retmat:
      fp = FlowPanel(border='double',spacing='small')
      if r[1]==1:
        tstr = ' team'
      else:   
        tstr = ' teams'
      fp.add_component(Label(text=r[0] + ': ' + str(r[1]) + tstr,
               bold=True,spacing_above='none',spacing_below='none'
               ))
      for z in range(r[1]):
        fp.add_component(Label(text=r[2][z],spacing_above='none',
                  italic=True,spacing_below='none'))
      self.p2teams.add_component(fp)
      self.p2teams.add_component(Spacer(height=2))
    

