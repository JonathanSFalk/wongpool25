import anvil.facebook.auth
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
from datetime import datetime, timedelta
import pytz
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


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
    result = player_list()
    lookup = []
    retn = []
    ldict = {}
    for r in result:
        lookup.append(r['lookup'])
        ldict[r['lookup']] = [r['plahman'],r['fullname']]
    urlsched = 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate={}&endDate={}'.format(date,date)
    print(urlsched)
    schedule = anvil.http.request(urlsched,json=True)
    if len(schedule['dates'])==0:
        return retn
    for games in schedule['dates'][0]['games']:
        print(games['gamePk'])
        dh = games['doubleHeader']
        if games['gameType']=='R':
            thegameurl = 'http://statsapi.mlb.com/api/v1/game/{}/boxscore'.format(games['gamePk'])
            thegame = anvil.http.request(thegameurl,json=True)
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

@anvil.server.background_task
def update():
    anvil.server.task_state['Progress'] = 'Updating'
    timerun = datetime.now()
    edt_timerun = pytz.timezone("UTC").localize(timerun).astimezone(pytz.timezone('America/New_York'))
    fdate = datetime.strftime(timerun - timedelta(days=1),'%Y-%m-%d')
    hrlist=[]
    daterange = [fdate]
    #daterange = ['2023-03-30','2023-04-01']
    print(daterange)
    dr_to_print = ''
    for d in daterange:
        h = get_all_homers(d)
        dr_to_print = dr_to_print + '\t' + d
        hrlist.extend(h)
    emailbody = 'Update run on ' + edt_timerun.strftime("%m/%d/%Y, %H:%M:%S") + \
    '\r\n' + 'Range of dates run: ' + dr_to_print + '\r\n\r\n'
    print(emailbody)
    for hr in hrlist:
        plahman = hr[0]
        hometeam = get_team_abbrev(hr[3])
        gid = hometeam + hr[1].replace('-','')
        date = hr[1]
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
        result = get_homer(plahman,gid)
        fullname = fn(plahman)
        if result is None:
            update_dict={'date':date,'homers':homers,'plahman':plahman,'gameid':gid,'last_updated':edt_timerun}
            write_to_homers(update_dict)
            emailbody = emailbody + fullname + " on " + date + " hit " + str(homers) + "\n"
        elif result['homers'] != homers:
            result['homers'] = homers
            emailbody = emailbody + fullname + " on " + date + " changed to " + str(homers) + "\n"
        else:
            emailbody = emailbody + "[Unchanged: " + fullname + " on " + date + " hit " + str(homers) + "]\n"
    if hrlist==[]:
        emailbody = emailbody + 'No Homers Hit'

    sg = SendGridAPIClient(get_my_secret('sendgrid'))
    message = Mail(
    from_email='webmaster@wongpool.com',
    to_emails=['jonathansfalk@gmail.com'],  
#    to_emails=['jonathansfalk@gmail.com','drwfood@hotmail.com'],
    subject='Wongpool Update Report',
    plain_text_content=emailbody)

    response = sg.send(message)
    players = player_list()
    for p in players:
       anvil.server.task_state['Progress'] = p['plahman']
       response = check(p) 
    teams = team_list()
    for t in teams:
        check_a_team(t)
        anvil.server.task_state['Progress'] = t['Teamname']
    response = nocrash()

    return 

def nocrash():
    sg = SendGridAPIClient(get_my_secret('sendgrid'))
    message = Mail(
    from_email='webmaster@wongpool.com',
    to_emails=['jonathansfalk@gmail.com'],
    subject='Wongpool Crash Report',
    plain_text_content="Update Program Completed")
    response = sg.send(message)
    return 
  

  
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
#  print(p['plahman'])
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
#    print(t['Teamname'])
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

@anvil.server.callable
def start_update():
  task = anvil.server.launch_background_task('update')
  therow = app_tables.update.get(Counter='Only')
  therow['Id'] = task.get_id()
  print(therow['Id'])

  
@anvil.server.http_endpoint("/results")
def results():
    task_id = app_tables.update.get(Counter='Only')['Id'] 
    print(task_id)
    task = anvil.server.get_background_task(task_id)
    status = task.get_termination_status()
    responses = {
        None: {"status": 202, "body": "Running: " + task.get_state().get("Progress", None) },
        "failed": {"status": 500, "body": "An error occurred whilst generating your dataset. Get Owen to have a look."},
        "killed": {"status": 500, "body": "The background task to generate your dataset has been killed. Get Owen to have a look."},
        "missing": {"status": 500,"body": "The background task to generate your dataset is AWOL. Get Owen to have a look"},
        "completed": {"status": 200, "body": task.get_state().get("Progress", None)}
    }
    return anvil.server.HttpResponse(**responses[status])  

  