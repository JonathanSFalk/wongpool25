import anvil.secrets
import anvil.stripe
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.http
from . import wfs
import requests
import json
import datetime


@anvil.server.callable
def lupdate():
  lupdate = app_tables.homers.search(tables.order_by('last_updated', ascending=False))[0]
  return lupdate['last_updated'].strftime("%m/%d, %H:%M EDT")

@anvil.server.callable
def get_team_abbrev(code):
  return app_tables.mlbteams.get(teamid=code)['teamcode']

@anvil.server.callable
def get_my_secret(key):
  return anvil.secrets.get_secret(key)

@anvil.server.callable
def write_to_homers(data):  
        result = app_tables.homers.get(q.all_of(plahman=data['plahman'],gameid=data['gameid']))
        fn = app_tables.players.get(plahman=data['plahman'])['fullname']
        if result is None:
            app_tables.homers.add_row(date=data['date'],gameid=data['gameid'],homers=data['homers'],
                           last_updated=data['last_updated'],plahman=data['plahman'])
            emailbody = fn + " on " + data['date'] + " hit " + str(data['homers']) + "\n"
        elif result['homers'] != data['homers']:
            result['homers'] = data['homers']
            emailbody = fn + " on " + data['date'] + " changed to " + str(data['homers']) + "\n"
        else:
            emailbody = "[Unchanged: " + fn + " on " + data['date'] + " hit " + str(data['homers']) + "]\n"
        return emailbody
            
@anvil.server.callable
def get_http(url):
  return anvil.http.request(url,json=True)

def get_all_homers(date):
    result = app_tables.players.search()    
    lookup = []
    retn = []
    ldict = {}
    for r in result:
        lookup.append(r['lookup'])
        ldict[r['lookup']] = [r['plahman'],r['fullname']]    
    urlsched = 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate={}&endDate={}'.format(date,date)
    response = requests.get(urlsched)
    schedule = json.loads(response.text)
    for games in schedule['dates'][0]['games']:
        dh = games['doubleHeader']
        if games['gameType']=='R':
            thegameurl = 'http://statsapi.mlb.com/api/v1/game/{}/boxscore'.format(games['gamePk'])
            response = requests.get(thegameurl)
            thegame = json.loads(response.text)
            app_tables.gamejsons.add_row(Date=date,GameID=str(games['gamePk']),JSON=thegame)
#            for l in lookup:
#                if 'ID' + str(l) in thegame['teams']['home']['players']:
#                    homers = thegame['teams']['home']['players']['ID' + str(l)]['stats']['batting'].get('homeRuns',0)
#                    if homers > 0:
#                        gn = games['gameNumber']
#                        home = thegame['teams']['home']['team']['id']
#                        retn.append([ldict[l][0],date,gn,home,homers,dh])
#                elif 'ID' + str(l) in thegame['teams']['away']['players']:
#                    homers = thegame['teams']['away']['players']['ID' + str(l)]['stats']['batting'].get('homeRuns',0)
#                    if homers > 0:
#                        gn = games['gameNumber']
#                        home = thegame['teams']['home']['team']['id']
#                        retn.append([ldict[l][0],date,gn,home,homers,dh])
#    return retn
    return 

@anvil.server.callable  
def update():
    emailbody = ""
    timerun = datetime.datetime.now()
    rundays = 1
    daterange=[]
#    engine=dbconn.engine()
#    for i in range(1,rundays+1):
#    	daterange.append((timerun + datetime.timedelta(days=-i)).strftime("%m/%d/%Y"))
    hrlist=[]
    daterange = ['2020-09-15']
  
    for d in daterange:
    	h = get_all_homers(d)
    	print(d,h)
    	hrlist.extend(h)

    for hr in hrlist:
        plahman = hr[0]
        print(hr)
        hometeam = app_tables.mlbteams.get(teamcode=hr[3])['tname_short']
        gid = hometeam + hr[1][6:] + hr[1][0:2] + hr[1][3:5]
        date = hr[1][6:] + '-' + hr[1][0:2] + '-' + hr[1][3:5]
            # Second game of doubleheader
        if hr[2]==2:
            gid = gid + '2'
            # first game of doubleheader
        elif hr[2]==1 and (hr[5]=="Y" or hr[5]=="S"):
            gid = gid + '1'
            #single game
        else:
            gid = gid + '0'
        homers = hr[4]
        result = app_tables.homers.get(q.all_of(plahman=plahman,gameid=gameid))
        fn = app_tables.players.get(plahman=plahman)['fullname']
        if result is None:
            app_tables.homers.add_row(date=date,gameid=gid,homers=homers,plahman=plahman,last_updated=timerun)           
            z = update_phmdat(app_tables.homers.get(plahman=plahman,gameid=gameid),0)            
            emailbody = emailbody + fn + " on " + date + " hit " + str(homers) + "\n"
        elif result['homers'] != homers:
            z = update_phmdat(result,homers-2*result['homers'])
            
            result['homers'] = homers
            emailbody = emailbody + fn + " on " + date + " changed to " + str(homers) + "\n"
        else:
            emailbody = emailbody + "[Unchanged: " + fn + " on " + date + " hit " + str(homers) + "]\n"


    outtab= "Program ran at " + timerun.strftime("%I:%M %p") + '\n'
    outtab = outtab + '\n' + emailbody
    if emailbody=="":
        outtab = outtab + "No Homers Added"
    return emailbody

@anvil.server.callable
def update_phmdat(homer, change):
  '''Adds player-game to phmdat table'''
  print(homer['date'],homer['plahman'],homer['gameid'])
  month = int(homer['date'][5:7])
  if month==3:
    month=4
  elif month==10:
    month=9
  theplayer = app_tables.phmdat.search(plahman=homer['plahman'])  
  months = ["April","May","June","July","August","September"]
  if theplayer is None:
     nothin = app_tables.phmdat.add_row(
        Player = theplayer,
        pnum = theplayer['pnum'],
        plast = theplayer['plast'],
        plahman = theplayer['plahman'],
        lookup = theplayer['lookup'],
        fullname=theplayer['fullname'])	
     theplayer = app_tables.phmdat.get(Player=theplayer)
     theplayer["April"] = 0
     theplayer["May"] = 0
     theplayer["June"] = 0
     theplayer["July"] = 0
     theplayer["August"] = 0
     theplayer["September"] = 0
     theplayer["Total"] = 0       
  theplayer[months[month-4]] += homer['homers'] + change
  theplayer['Total'] += homer['homers'] + change
  return 

@anvil.server.callable
def check(p):
  '''Assumes the homer list is correct and checks phmdat tables'''
  print(p['plahman'])
  h = [0,0,0,0,0,0,0]
  hlist = app_tables.homers.search(plahman=p['plahman'])
  if hlist is not None:
    for hr in hlist:
      month = int(hr['date'][5:7])
      if month==3:
        month=4
      elif month==10:
        month=9
      h[month-4] += hr['homers']
    h[6] = sum(h[0:6])
  c = app_tables.phmdat.get(plahman=p['plahman'])
  if c is None:
    print('Row missing for ' + p['plahman'])
    app_tables.phmdat.add_row(
             Player = p,
      pnum = p['pnum'],
      plast = p['plast'],
      plahman = p['plahman'],
      lookup = p['lookup'],
      fullname = p['fullname'],
      April = h[0], May=h[1], June=h[2],July=h[3],August=h[4],September=h[5],Total=sum(h) 
    )
  elif h != [c['April'],c['May'],c['June'],c['July'],c['August'],c['September'],c['Total']]:
    print(h,[c['April'],c['May'],c['June'],c['July'],c['August'],c['September'],c['Total']])
    print('Correcting ' + p['fullname'])
    c['April'] = h[0]
    c['May'] = h[1]
    c['June'] = h[2]
    c['July'] = h[3]
    c['August'] = h[4]
    c['September'] = h[5]
    c['Total'] = sum(h[0:6])  
      
@anvil.server.callable
def check_a_team(t):
    print(t['Teamname'])
    mdict = {4:'April',5:'May',6:'June',7:'July',8:'August',9:'September','Total':'Total'}
    for m in mdict.keys():
      totalx = wfs.total(t,mdict[m])
      if t[mdict[m]] != totalx:
        print('Correcting ' + t['Teamname'] + ' ' + mdict[m] + ' to ' + str(totalx))
        t[mdict[m]] = totalx
        
@anvil.server.callable
def player_list():
  return app_tables.players.search(tables.order_by("pnum"))

@anvil.server.callable
def team_list():
  return app_tables.teams.search()


@anvil.server.callable
def get_homer(player,game):
  return app_tables.homers.get(q.all_of(plahman=player,gameid=game))


@anvil.server.callable
def fn(player):
  return app_tables.players.get(plahman=player)['fullname']
                               