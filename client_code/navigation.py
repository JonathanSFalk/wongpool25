import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from .Homers import Homers
from .Players import Players
from .PlayersToTeams import PlayersToTeams
from .Standings import Standings
from .HomeContent import HomeContent
from .WhosHot import WhosHot
from .Analytics import Analytics
from .Prizes import Prizes

home_form = None

def get_form():
  if not home_form:
    raise Exception("You must set the home form first.")
    
  return home_form
            
def go_homers():
  set_title("Homers")
  set_active_nav('homers')  
  form = get_form()
  form.load_component(Homers())

def go_prizes():
  set_title("Prizes")
  set_active_nav('prizes')
  form = get_form()
  form.load_component(Prizes())
  
def go_home():
  set_active_nav('home')
  set_title("")
  form = get_form()
  form.load_component(HomeContent())

def go_players():
  set_active_nav('players')
  set_title("Players")
  form = get_form()
  form.load_component(Players())

def go_p2teams():
  set_active_nav('p2teams')
  set_title("Players --> Teams")
  form = get_form()
  form.load_component(PlayersToTeams())
 
def go_standings():
  set_active_nav('standings')
  set_title("Standings")
  form = get_form()
  form.load_component(Standings())

def go_teams():
  set_active_nav('teams')
  set_title("Teams")
  form = get_form()
  form.load_component(Teams())
  
def go_hot():
  set_active_nav('hot')
  set_title("Who's Hot")
  form = get_form()
  form.load_component(WhosHot())
  
def go_Analytics():
  set_active_nav('Analytics')
  set_title('Total Homers')
  form = get_form()
  form.load_component(Analytics())
  
def set_active_nav(state):
  form = get_form()
  form.set_active_nav(state)
  
def set_title(text):
  form = get_form()
  base_title = form.base_title
  
  if text:
    form.label_title.text = base_title + " - " +  text
  else:
    form.label_title.text = base_title

    
def require_account():
    user = anvil.users.get_user()
    if user:
      return user
    
    user = anvil.users.login_with_form(allow_cancel=True)
    form = get_form()
    form.set_account_state(user)
    return user
    