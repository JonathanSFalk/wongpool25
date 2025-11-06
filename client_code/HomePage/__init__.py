from ._anvil_designer import HomePageTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import date
import anvil.users
from .. import navigation
from .. import data_access
  

class HomePage(HomePageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run when the form opens.
    self.link_login.visible = False
    self.link_register.visible = False
    self.base_title = self.label_title.text
    lupdate = data_access.get_lupdate()
    self.lupdate.text = "Last Update: " + lupdate
    user = None
    self.set_account_state(user)
    navigation.home_form = self
    navigation.go_home()
    

  def link_homers_click(self, **event_args):
    self.call_js('hideSidebarIfModal')
    navigation.go_homers()


    
  def link_home_click(self, **event_args):
    self.call_js('hideSidebarIfModal')
    navigation.go_home()


  def link_players_click(self, **event_args):
    self.call_js('hideSidebarIfModal')
    navigation.go_players()
    

  def link_teams_click(self, **event_args):
    self.call_js('hideSidebarIfModal')
    navigation.go_teams()

  def link_standings_click(self, **event_args):
    self.call_js('hideSidebarIfModal')
    navigation.go_standings()
    
  def link_hot_click(self, **event_args):
    self.call_js('hideSidebarIfModal')
    navigation.go_hot()
    
  def link_Players2Teams_click(self, **event_args):
    self.call_js('hideSidebarIfModal')
    navigation.go_p2teams()
    
  def Analytics_click(self, **event_args):
    self.call_js('hideSidebarIfModal')
    navigation.go_Analytics()
    
  def link_register_click(self, **event_args):
    user = anvil.users.signup_with_form(allow_cancel=True)
    self.set_account_state(user)
    navigation.go_home()

  def link_login_click(self, **event_args):
    user = anvil.users.login_with_form(allow_cancel=True)
    self.set_account_state(user)
    navigation.go_home()

  def link_logout_click(self, **event_args):
    anvil.users.logout()
    self.set_account_state(None)
    data_access.logout()
    navigation.go_home()
  
  def set_active_nav(self, state):
    self.link_home.role = 'selected' if state == 'home' else None
    self.link_homers.role = 'selected' if state == 'homers' else None
    self.link_players.role = 'selected' if state == 'players' else None
    self.link_Players2Teams.role = 'selected' if state == 'players2teams' else None
    self.link_standings.role = 'selected' if state == 'standings' else None
    self.link_hot.role = 'selected' if state == 'hot' else None
    self.Analytics.role = 'selected' if state=="Analytics" else None
   
  def load_component(self, cmpt):
    self.card_content.clear()
    self.card_content.add_component(cmpt)
    
#    if data_access.the_user():
    self.set_account_state(None)

  def set_account_state(self, user):
#    self.link_account.visible = user is not None
#    self.link_logout.visible = user is not None
    self.link_login.visible = False
    self.link_register.visible = False

  def prizes_click(self, **event_args):
    self.call_js('hideSidebarIfModal')
    navigation.go_prizes()


  
  
    



 





