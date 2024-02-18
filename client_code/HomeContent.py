from ._anvil_designer import HomeContentTemplate
from anvil import *
import anvil.facebook.auth
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from . import data_access

class HomeContent(HomeContentTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    mstands, cstands, tstands = data_access.stands()
    mpanel = []
    cpanel = []
    tpanel = []
    for r in range(0,len(mstands)):
      col1 = mstands[r].split('/')[0]
      col2 = mstands[r].split('/')[1]
      mpanel.append({'team':col1,'value':col2})
    for r in range(0,len(cstands)):  
      col3 = cstands[r].split('/')[0]
      col4 = cstands[r].split('/')[1]
      cpanel.append({'team':col3,'value':col4})
    for r in range(0,len(tstands)):  
      col5 = tstands[r].split('/')[0]
      col6 = tstands[r].split('/')[1]
      tpanel.append({'team':col5,'value':col6})
    self.winpanel.items = mpanel
    self.monthpanel.items = cpanel
    self.totpanel.items = tpanel

    # Any code you write here will run when the form opens.