from ._anvil_designer import signupTemplate
from anvil import *
import anvil.facebook.auth
import stripe.checkout
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
import custom_signup.login_flow
from anvil.tables import app_tables

class signup(signupTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
  def focus_email(self, **kws):
     """Focus on the email box."""
     self.email_box.focus()


  def close_alert(self, **kws):
    """Close any alert we might be in with True value."""
    self.raise_event('x-close-alert', value=True)

  def login_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    custom_signup.login_flow.login_with_form()
