from ._anvil_designer import AnalyticsTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import stripe.checkout
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..teamrow import teamrow

class Analytics(AnalyticsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.drop_down_1.selected_value="Total"
    hrteam = anvil.server.call('standings','Total', False)
    hrs = [x['Total'] for x in hrteam]
    tm = [x['Teamname'] for x in hrteam]
    self.plot_1.data = [
      go.Bar(
        y = hrs,
        x = tm,
        marker=dict(color='#EB89B5'))     
    ]
    self.plot_1.layout.xaxis.showticklabels=False
    self.plot_1.layout.title="Current Total Standings"
    

  def drop_down_1_change(self, **event_args):
    hrteam = anvil.server.call('standings',self.drop_down_1.selected_value,False)
    hrs = [x[self.drop_down_1.selected_value] for x in hrteam]
    tm = [x['Teamname'] for x in hrteam]
    self.plot_1.data = [
      go.Bar(
        y = hrs,
        x = tm,
        marker=dict(color='#EB89B5'))     
    ]
    self.plot_1.layout.xaxis.showticklabels=False
    self.plot_1.layout.title=self.drop_down_1.selected_value + " Standings"
    self.plot_1.redraw()

  def plot_1_click(self, points, **event_args):
    team = points[0]['x']
    picks = anvil.server.call('picks',team)
    itms = []
    for i in range(0,8):
      itms.append([picks[i]['player'],picks[i][self.drop_down_1.selected_value]])
    itms.sort(key = lambda x:x[1],reverse=True)
    def strike(x):
      r = ''
      for c in str(x):
        r = r + c + '\u0336'
      return r
    itms[6][0] = strike(itms[6][0])
    itms[6][1] = strike(itms[6][1])
    itms[7][0] = strike(itms[7][0])
    itms[7][1] = strike(itms[7][1])
    itms.append(['Total',itms[0][1]+itms[1][1]+itms[2][1]+itms[3][1]+itms[4][1]+itms[5][1]])
    t = RepeatingPanel(items=itms,item_template=teamrow)
    alert(content=t,title=team)
    

