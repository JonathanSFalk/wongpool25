import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import *
import anvil.facebook.auth
import stripe.checkout
from . import data_access
from .signup import signup
import json
import datetime

print(anvil.app.environment.name)
###### AFTER END OF SEASON UPDATE WFS LINE 104
##### At beginning of season remove return from update module

def get_all_homers(date):
    result = anvil.server.call('player_list')
    lookup = []
    retn = []
    ldict = {}
    for r in result:
        lookup.append(r['lookup'])
        ldict[r['lookup']] = [r['plahman'],r['fullname']]    
    urlsched = 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate={}&endDate={}'.format(date,date)
    schedule = anvil.server.call('get_http',urlsched)
    for games in schedule['dates'][0]['games']:
#        print(games['gamePk'])
        dh = games['doubleHeader']
        if games['gameType']=='R':
            thegameurl = 'http://statsapi.mlb.com/api/v1/game/{}/boxscore'.format(games['gamePk'])
            thegame = anvil.server.call('get_http',thegameurl)
            for l in lookup:
                if 'ID' + str(l) in thegame['teams']['home']['players']:
                    homers = thegame['teams']['home']['players']['ID' + str(l)]['stats']['batting'].get('homeRuns',0)
                    if homers > 0:
                        gn = games['gameNumber']
                        home = thegame['teams']['home']['team']['id']
                        retn.append([ldict[l][0],date,gn,home,homers,dh])
                elif 'ID' + str(l) in thegame['teams']['away']['players']:
                    homers = thegame['teams']['away']['players']['ID' + str(l)]['stats']['batting'].get('homeRuns',0)
                    if homers > 0:
                        gn = games['gameNumber']
                        home = thegame['teams']['home']['team']['id']
                        retn.append([ldict[l][0],date,gn,home,homers,dh])
    return retn

def signup_with_form():
  d = signup()

  while True:
    if not alert(d, title="Sign Up", buttons=[("Sign Up", True, 'primary'), ("Cancel", False)]):
      return
    
    if d.password_box.text != d.password_repeat_box.text:
      d.signup_err_lbl.text = 'Passwords do not match. Try again.'
      d.signup_err_lbl.visible = True
      continue
    
    err = anvil.server.call('_do_signup', d.email_box.text, d.name_box.text, d.password_box.text)
    if err is not None:
      d.signup_err_lbl.text = err
      d.signup_err_lbl.visible = True
    else:
#      alert(f"We have sent a confirmation email to {d.email_box.text}.\n\nCheck your email, and click on the link.")
      return
  


#def update():
#    timerun = datetime.datetime.now()
#    rundays = 1
#    daterange=[]
#    engine=dbconn.engine()
#    for i in range(1,rundays+1):
#    	daterange.append((timerun + datetime.timedelta(days=-i)).strftime("%m/%d/%Y"))
 #   hrlist=[]
 #   daterange = ['2020-09-15']
  
#    for d in daterange:
#    	h = get_all_homers(d)
#    	hrlist.extend(h)
##       plahman = hr[0]
#        print(hr)
#        hometeam = app_tables.mlbteams.get(teamid=hr[3])['teamcode']
#        gid = hometeam + hr[1].replace('-','')
#        date = hr[1]
#            # Second game of doubleheader
#        if hr[2]==2:
#            gid = gid + '2'
#            # first game of doubleheader
#        elif hr[2]==1 and (hr[5]=="Y" or hr[5]=="S"):
#            gid = gid + '1'
#            #single game
#        else:
#            gid = gid + '0'
#        homers = hr[4]
#       update_dict={'date':date,'homers':homers,'plahman':plahman,'gameid':gid,'last_updated':timerun}
#        emailbody = anvil.server.call('write_to_homers',update_dict)
#        if emailbody !='':
#            del update_dict['last_updated']
#            app_tables.updatwhile notes.add_row(Update=update_dict,RunTime=timerun)
#        else:  
#            app_tables.updates.add_row(Update='Nothing to Update',RunTime=timerun)
#    return
  

#login_class=-1
#while login_class==-1 or login_class==0:
#    login_class = alert('Welcome to Wongpool 2023\r\n Sign Up, Log in or continue as guest',large=True,
#                    buttons=[('Guest',0),('Signup',1),("Login",2)])
#    if login_class==0:
#        alert('There is nothing to see as a guest before the season starts.\r\nTo pick a team, create an ID and log in as a user',large=True)
#    elif login_class==1:
#      signup_with_form()
#      user = anvil.users.get_user(allow_remembered=True)
#      if user is None:
#        user = 'Guest'
#        login_class = 0
##    else:
#      anvil.users.login_with_form(allow_cancel=True,allow_remembered=True)
#      user = anvil.users.get_user(allow_remembered=True)
#      if user is None: 
#         user='Guest'
#         login_class = 0 
#  
 
#update_text = update()
#z=anvil.server.call('check')
#tlist = anvil.server.call('team_list')
#for t in tlist:
#  x = anvil.server.call('check_a_team',t)
#open_form('Analytics')
#x = anvil.server.call('fill_in_players')
#open_form('HomePage')
signup_with_form()
if user['email'] == 'me':
  open_form('Form1')
open_form('TeamPicker')
#anvil.server.call('start_update')
#open_form('SplashScreen')
#pdf = anvil.server.call('pdf2')
#anvil.media.download(pdf)


