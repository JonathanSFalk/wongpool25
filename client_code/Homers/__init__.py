from ._anvil_designer import HomersTemplate
from anvil import *
import anvil.facebook.auth
import stripe.checkout
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.server
import anvil.tables as tables 
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import date, timedelta


def pdict():
    pdt = app_tables.players.search(tables.order_by('plast'))

    pnames = {}
    pnums = {}
    plahman = {}
    psort = {}
    i = 1
    for p in pdt:
      pnames[p['fullname']] = p['pnum']
      pnums[str(p['pnum'])] = p['fullname']
      plahman[p['plahman']] = p['fullname']
      psort[p['fullname']] = i
      i += 1
    return pnames,pnums,plahman,psort

pnames, pnums, plahman, psort = pdict()

class Homers(HomersTemplate):
  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.text_box_1.text = 1


    # Any code you write here will run when the form opens.
  
  
  def button_1_click(self, **event_args):
    df = self.date_picker_1.date
    dt = df + timedelta(days=self.text_box_1.text)
    homerlist = self.listhomers(df,dt,plahman)
    self.repeating_panel_1.items = homerlist
    self.data_grid_1.visible = True
    self.refresh_data_bindings()
         
  def listhomers(self,df,dt,plahman):
    datealphas = '{:04d}'.format(df.year) + '-' + '{:02d}'.format(df.month)  + '-' + '{:02d}'.format(df.day)
    datealphat = '{:04d}'.format(df.year) + '-' + '{:02d}'.format(dt.month)  + '-' +'{:02d}'.format(dt.day)
    retmat=[]
    hlist = app_tables.homers.search(tables.order_by('date'),date=q.between(
      min=datealphas,max=datealphat,max_inclusive=True))
    for x in hlist:
            if x['gameid'][-1]=="0":
                adder = ""
            elif x['gameid'][-1]=="1":
                adder = " (First Game)"
            else:
                adder = " (Second Game)"
            retmat.append(dict(player=plahman[x['plahman']],
                               date=x['date']+adder,hr=x['homers']))    
    return retmat

  def button_2_click(self, **event_args): 
    homerlist = self.repeating_panel_1.items
    self.repeating_panel_1.items = sorted(homerlist, key = lambda i: i['date'])
    self.refresh_data_bindings()

  def button_3_click(self, **event_args):
    homerlist = self.repeating_panel_1.items
    self.repeating_panel_1.items = sorted(homerlist, key = lambda i: psort[i['player']])
    self.refresh_data_bindings()

  def date_picker_1_change(self, **event_args):
    """This method is called when the selected date changes"""
    pass

 



