from ._anvil_designer import WhosHotTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from . import data_access

class WhosHot(WhosHotTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    to_table = [rows for rows in data_access.get_hothomers()]
    self.repeating_panel_1.items = to_table
    # Any code you write here will run when the form opens.