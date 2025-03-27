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
from datetime import date, timedelta


def init():
    pdt = app_tables.players.search()

    pnames = {}
    for p in pdt:
        pnames[p['fullname']] = p['pnum']

    pnums = {}
    for p in pdt:
        pnums[p['pnum']] = p['fullname']

    plahman = {}
    for p in pdt:
        plahman[p['plahman']] = p['fullname']

    psort = {}
    xs = app_tables.players.search(tables.order_by('plast'))
    i = 1
    for x in xs:
        psort[x['fullname']] = i
        i += 1

    hdt = app_tables.homers.search()
    tdt = app_tables.teams.search()

    if len(hdt)>0:
       gid = [r['date'] for r in app_tables.homers.search()]
       gid.sort()
       dmx = gid[len(gid)-1]
       print(dmx)
       dmxstr = date(int(dmx[0:4]),int(dmx[5:7]),int(dmx[9:])).strftime("%B %d").lstrip("0").replace(" 0"," ")
       dmx = date(int(dmx[0:4]),int(dmx[5:7]),int(dmx[9:]))
    else:
        dmxstr = "4/01"
        dmx = date(2021,4,1)

    return pnames,pnums,plahman,psort

@anvil.server.callable
def standings(colname, asc):
  return app_tables.teams.search(tables.order_by(colname,ascending=asc))

@anvil.server.callable
def players(colname, asc):
  return app_tables.phmdat.search(tables.order_by(colname,ascending=asc))

@anvil.server.callable
def index():
   results = getresults()
   mstands = [x[1] for x in results if x[0]==1]
   cstands = [x[1] for x in results if x[0]==2]
   tstands = [x[1] for x in results if x[0]==3]
   numrows = max(len(mstands),len(cstands),len(tstands))
#   mstands.extend(["  /  "] * (numrows - len(mstands)))
#   cstands.extend(["  /  "] * (numrows - len(cstands)))
#   tstands.extend(["  /  "] * (numrows - len(tstands)))
   return mstands,cstands,tstands 

@anvil.server.callable  
def hothomers(): 
    gid = app_tables.homers.search(tables.order_by('date',ascending=False))[0]['date']   
    if len(gid)>0:
      dmxstr = gid
      dmx = date(int(dmxstr[0:4]),int(dmxstr[5:7]),int(dmxstr[8:]))
    else:
      dmx = date(2021,4,1)
      dmxstr = '2021-04-01'
    startdate = dmx - timedelta(days = 9)
    datealpha = '{:04d}'.format(startdate.year) + '-' + '{:02d}'.format(startdate.month) + '-' + '{:02d}'.format(startdate.day)
    pt = {}
    for x in app_tables.homers.search(date=q.between(datealpha,dmxstr,max_inclusive=True)):
       fname = app_tables.players.get(plahman=x['plahman'])
       if fname['fullname'] in pt:
        pt[fname['fullname']] += x['homers']
       else:
        pt[fname['fullname']] = x['homers']
    hlist = sorted(pt.items(), key=lambda arg: -arg[1])
    for h in range(len(hlist)):
      hlist[h] = dict(player=hlist[h][0],hr=hlist[h][1])
    return hlist  

def getresults():
    dmax = app_tables.homers.search(tables.order_by('date',ascending=False))[0]['date']
    results = []
    months = ("April: ","May: ","June: ","July: ","Aug: ","Sept: ")
    last_month = int(dmax[5:7])
    # New line if the season ends in September
    # Comment out when season begind
#    last_month = 10
    if last_month==3:
      last_month=4
    if last_month==10:
      last_month=9
    # Comment out ofter last games  
#      last_month = 10  
    # Create monthly winners: results code 1
    for i in range(4,last_month):
        standings = monthstandings(i)
        best = standings[0][2]
        winners = [x[1] for x in standings if x[2] == best]
        results.append([1,months[i - 4] + ", ".join(winners) + '/' + str(best)])
    # create Current month standings: results code 2
    standings = monthstandings(min(max(last_month,4),9))
    results.extend(top5(2,standings))

    # Create Total standings: results code 3
    standings = monthstandings("Total")
    results.extend(top5(3,standings))
    return results


def top6of8(listof8):
    assert len(listof8) == 8,"Gotta send 8"
    z = sorted(listof8,reverse=True)
    return z[0] + z[1] + z[2] + z[3] + z[4] + z[5]
  
@anvil.server.callable
def total(team,month):
    mdict = {4:'April',5:'May',6:'June',7:'July',8:'August',9:'September','Total':'Total'}
    plist = [team['P1'],team['P2'],team['P3'],team['P4'],team['P5'],team['P6'],team['P7'],team['P8']]
    mlist = []
    for j in plist:
        mlist.append(app_tables.phmdat.get(pnum=j)[month])
    return top6of8(mlist)     

def monthstandings(month):
    # makes standings for month.  Last Month is called "Total"
    mdict = {4:'April',5:'May',6:'June',7:'July',8:'August',9:'September','Total':'Total'}
    mstandings = []
    teamsort = sorted([x['Teamname'] for x in app_tables.teams.search()])
    for t in app_tables.teams.search():
    #    print(month,t['Teamname'],t[mdict[month]])
        mstandings.append([t['Teamnum'],t['Teamname'],t[mdict[month]]])
      
    #print(mstandings)
    #print(teamsort)
    return sorted(mstandings,key=lambda x: (-x[2] * 10000 + teamsort.index(x[1])))

def top5(rowtype,standlist):
    # makes an appropriate list from a sorted standing list
    best = standlist[0][2]
    tiercount = [len([x for x in standlist if x[2]==best])]
    while sum(tiercount)<5:
        best=standlist[sum(tiercount)][2]
        tiercount.append(len([x for x in standlist if x[2]==best]))
    index = 0
    result=[]
    for i in tiercount:
        for j in range(index,index+i):
            result.append([rowtype,str(index+1)+". " + standlist[j][1] + "/" + str(standlist[j][2])])
        index = index + i
    return result

@anvil.server.callable
def pdict():
  pdt = app_tables.players.search(tables.order_by('plast'))
  pnames = {}
  pnums = {}
  plahman = {}
  psort =  {}
  i = 1
  for p in pdt:
    pnames[p['fullname']] = p['pnum']
    pnums[str(p['pnum'])] = p['fullname']
    plahman[p['plahman']] = p['fullname']
    psort[p['fullname']] = i
    i += 1
  return pnames,pnums,plahman,psort

@anvil.server.callable
def get_pdict():
  _,pnums,_,_ = pdict()
  return pnums

@anvil.server.callable
def save_team(owner,name,team):
  tnums = [r['Teamnum'] for r in app_tables.teams.search()]
  tnums.sort()
  if tnums == []:
    nextnum = 1
  elif len(tnums) == tnums[len(tnums)-1]:
    nextnum = len(tnums)+1
  else:
    tset = set(tnums)
    nextnum = [x for x in range(1,len(tset)+1) if x not in tset][0]
  pnames,_,_,_ = pdict()
  nums = [0,0,0,0,0,0,0,0]
  for  i in range(0,8):
    nums[i] = pnames[team[i]]
  nums.sort()
  app_tables.teams.add_row(Teamname=name,Owner=owner,Teamnum=nextnum,
             P1=nums[0],P2=nums[1],P3=nums[2],P4=nums[3],
             P5=nums[4],P6=nums[5],P7=nums[6],P8=nums[7],April=0,May=0,June=0,July=0,August=0,September=0,Total=0)
  return                         


@anvil.server.callable
def picks(team):
  retmat=[]
  matrix = [[0 for i in range(8)] for j in range(7)]
  tm = app_tables.teams.get(Teamname=team)
  for p in range(1,9):
    player = tm['P'+str(p)]
    print(player)
    prow = app_tables.phmdat.get(pnum=player)
    
    matrix[0][p-1] = prow['April']
    matrix[1][p-1] = prow['May']
    matrix[2][p-1] = prow['June']
    matrix[3][p-1] = prow['July']
    matrix[4][p-1] = prow['August']
    matrix[5][p-1] = prow['September']
    matrix[6][p-1] = prow['Total']            
    retmat.append(dict(player=str(player) + '. ' + prow['fullname'],
                      April=prow['April'],May=prow['May'],June=prow['June'],July=prow['July'],
                      August=prow['August'],September=prow['September'],Total=prow['Total']))
  total = [0,0,0,0,0,0,0]
  for i in range(7):
     total[i] = top6of8(matrix[i])
  retmat.append(dict(player='Total',April=total[0],May=total[1],June=total[2],
                       July=total[3],August=total[4],September=total[5],Total=total[6]))
  return retmat
  
@anvil.server.callable
def p2team():
    players = app_tables.players.search()
    retmat = []
    #Code fills the teams; to be used after all the teams are in
    #for p in players:
     # pnum = p['pnum']
      #the_teams = [r['Teamname'] for r in 
       #    app_tables.teams.search(q.any_of(P1=pnum,P2=pnum,
      #P3=pnum,P4=pnum,P5=pnum,P6=pnum,P7=pnum,P8=pnum))]
      #retmat.append([p['fullname'],len(the_teams),the_teams])  
      ## This line populates the 'teams' column.  To be used only before the season starts
 #     p['teams'] = the_teams
    for p in players:
      pnum = p['pnum']
      retmat.append([p['fullname'],len(p['teams']),p['teams']])
  
    retmat.sort(key=lambda x:-x[1])
    return retmat    

