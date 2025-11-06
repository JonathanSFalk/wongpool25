import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.pdf
import bcrypt
import json

@anvil.server.callable
def teamlist():
  z = app_tables.teams.search()
  rtn = []
  for t in z:
    print(t['Owner'])
    e = app_tables.users.search(owner=t['email'])
    for em in e:
      print(em['email'])
      zz = em['email']    
    rtn.append([zz,t['Teamname'],t['P1'],t['P2'],t['P3'],t['P4'],t['P5'],t['P6'],t['P7'],t['P8'],t['Teamnum']])
  rtn.sort(key= lambda x: int(x[10]))  
  return rtn  

@anvil.server.callable
def pdf2():
  pdf = anvil.pdf.render_form("Form1")
  return pdf

@anvil.server.callable
def create_pdf(teamrows):
  pdf = anvil.pdf.render_form("Print", teamrows)
  return pdf


@anvil.server.callable
def name_check(name):
  return app_tables.teams.get(Teamname=name) is None

@anvil.server.callable
def update_team(teamname,delete_switch,*newname):
  if delete_switch:
     result = app_tables.teams.get(Teamname=teamname).delete()
  else:
     result = app_tables.teams.get(Teamname=teamname)
     result['Teamname'] = newname[0]

@anvil.server.callable
def my_teams(owner):
  return app_tables.teams.search(Owner=owner)

def hash_password(password, salt):
  """Hash the password using bcrypt in a way that is compatible with Python 2 and 3."""
  if not isinstance(password, bytes):
    password = password.encode()
  if not isinstance(salt, bytes):
    salt = salt.encode()

  result = bcrypt.hashpw(password, salt)

  if isinstance(result, bytes):
    return result.decode('utf-8')

 

@anvil.server.callable
def fill_in_players():
  tofill = app_tables.players.search(plahman=None)
  for j in tofill:
    print(j['fullname'])
    rtn = anvil.server.call('get_data',str(j['lookup']))
    j['lookup'] = int(rtn[1])
    j['pbbref'] = rtn[2]
    j['plahman'] = rtn[0]
  zeroout = app_tables.players.search()
  for j in zeroout:
    j['teams'] = None
  return

@anvil.server.callable
def make_teams():
  allteams = app_tables.teams.search()
  for t in allteams:
    for i in ['P1','P2','P3','P4','P5','P6','P7','P8']:
      plr = t[i]
#      print(t['Teamnum'],i,plr)
      thatplayer = app_tables.players.get(pnum=plr)
      if thatplayer['teams'] is None:
        thatplayer['teams'] = [t['Teamnum']]
#        print(thatplayer['teams'])
      else:
        z = thatplayer['teams']
#        print('Before',thatplayer['teams'])
        z.append(t['Teamnum'])
        thatplayer['teams'] = z
#        print('After',thatplayer['teams'])
