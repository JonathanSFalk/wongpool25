import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from anvil import *

def _make_panel():
  panel = ColumnPanel()
  email_box = TextBox(placeholder="Email")
  password_box = TextBox(placeholder="Password", hide_text=True)
  panel.add_component(Label(text="Email"))
  panel.add_component(email_box)
  panel.add_component(Label(text="Password"))
  panel.add_component(password_box)
  return panel, email_box, password_box


def login_with_form():
  panel, email_box, password_box = _make_panel()
  result = alert(panel, title="Log In", buttons=[("Log In", True), ("Cancel", False)])
  if result:
    try:
      anvil.users.login_with_email(email_box.text, password_box.text)
    except anvil.users.AuthenticationFailed:
      alert("Invalid email or password.")

def signup_with_form():
  panel, email_box, password_box = _make_panel()
  result = alert(panel, title="Sign Up", buttons=[("Sign Up", True), ("Cancel", False)])
  if result:
    try:
      anvil.users.signup_with_email(email_box.text, password_box.text)
      alert("Check your email for a confirmation link. Once confirmed, come back and click Log In.")
    except anvil.users.UserExists:
      alert("That email is already registered.")