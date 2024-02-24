from ._anvil_designer import signupTemplate
from anvil import *
import anvil.server
import anvil.facebook.auth
import stripe.checkout
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import custom_signup.login_flow


class signup(signupTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.update_login_status()

    # Any code you write here will run before the form opens.

  def login_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    custom_signup.login_flow.login_with_form()
    self.update_login_status()

  def update_login_status(self):
    # Get the currently logged in user (if any)
    user = anvil.users.get_user()
    if user is None:
     self.login_status.text = "You are not logged in"
    else:
     self.login_status.text = f"You are logged in as {user['email']}"

  def signup_button_click(self, **event_args):
     custom_signup.login_flow.signup_with_form()
     print("Huh?") 
     self.update_login_status()
    
    