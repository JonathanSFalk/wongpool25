import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import *
from anvil import open_form
from . import data_access
import json
import datetime
import custom_signup.login_flow

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
open_form('SplashScreen')
custom_signup.login_flow.do_email_confirm_or_reset()
# Open Form1
open_form('signup')
user = anvil.users.get_user()
if user is not None:
  open_form('TeamPicker')
else:
  open_form('SplashScreen')
#update_text = update()
#z=anvil.server.call('check')
#tlist = anvil.server.call('team_list')
#for t in tlist:
#  x = anvil.server.call('check_a_team',t)
#open_form('Analytics')
#x = anvil.server.call('fill_in_players')
#open_form('HomePage')

#open_form('TeamPicker')
#anvil.server.call('start_update')

#pdf = anvil.server.call('pdf2')
#anvil.media.download(pdf)


