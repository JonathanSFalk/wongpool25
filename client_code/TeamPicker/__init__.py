from ._anvil_designer import TeamPickerTemplate
from anvil import *
import anvil.facebook.auth
import stripe.checkout
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import data_access
import time

class TeamPicker(TeamPickerTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.ws = anvil.js.window.innerWidth
    self.navbar_links.width = self.ws*.9
    self.user = anvil.users.get_user(allow_remembered=True)
    self.label_3.text = self.user['email']
    self.cap = 214
    self.label_2.text = f"Check a box to select that player.  Unchecking unselects.  Any legal team (8 players, Total {self.cap} or less) can be saved"
    self.pset = set()
    # Any code you write here will run when the form opens.
    players = anvil.server.call('player_list')
    for p in players:
      if self.ws>=500:
        self.grid_panel_1.width = self.ws
        num = 6
      else:
        num = 3
      col = (p['pnum']-1) % num
      row = (p['pnum']-1-col)/num
      cb = CheckBox(text=p['fullname']+":"+str(p['Weight']),tag=p['pnum'])
      cb.set_event_handler('change',self.pick_player)  
      self.grid_panel_1.add_component(
        cb,row=row,col_xs=col*12/num,width_xs=12/num)
    _ = self.top_panel(self.pset)
  
  def page_resize_event(self,page_size_px):
#    print("Page Resize Event - new size : "+str(page_size_px)+" px")
    return page_size_px
    
  def top_panel(self,theset):
    self.grid_panel_2.clear()
    thelist = [*theset,]
    unpicked = (None,0)
    for i in range(len(thelist),8):
      thelist.append((None,0))
    thelist.sort(key=lambda x: -x[1])    
    ptag = 0
    numplayers = 0
    for d in range(0,8):
      col = d % 4
      row = (d-col)/4
      if thelist[d][0] is not None:
        ptag += thelist[d][1]
        numplayers += 1
      self.grid_panel_2.add_component(
        TextBox(placeholder='Empty',text=thelist[d][0]),
        row=row,col_xs=col*3,width_xs=3,font_size=10)
    self.label_4.text= str(numplayers) + ' Players Selected'
    self.label_5.text ='HR Remaining: ' + str(self.cap-ptag)
    self.button_1.enabled = numplayers == 8 and ptag<=self.cap
    return
      
    
  def pick_player(self, **event_args):
    t = event_args['sender'].text
    item = t[0:t.find(':')],int(t[t.find(':')+1:])
    if event_args['sender'].checked == False:
      self.pset.remove(item)        
    else:
      if len(self.pset)==8:
        alert('You already have 8 players.  Uncheck one before adding this one.')
        event_args['sender'].checked = False
      else:
        self.pset.add(item)  
    _ = self.top_panel(self.pset)
    return

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    t = TextBox(placeholder="Enter Team Name Here")
    named = False
    while not named:
      name = alert(content=t,
        title="Team Name",dismissible=False)
      if not name or not t.text:
        n = Notification('No name set.  Save cancelled')
        n.show()
        break
      else:          
        named = anvil.server.call('name_check',t.text)
        if not named:
          n = Notification('Name already used. Try Another.',timeout=3)
          n.show()
          time.sleep(4)
#        if t.text.find('"')>-1:
#          n=Notification('Sorry. Double quotation marks not allowed in name.',timeout=3)
#          n.show()
#          named = False
    if named:
      tm = [*self.pset,]
      tm.sort(key=lambda x: -x[1])
      tm = [x[0] for x in tm]
      anvil.server.call('save_team',self.user['email'],t.text,tm)
      n = Notification(f"<b>{t.text}</b> has been saved.")
      n.show()
    return
  
  def button_3_click(self, **event_args):
    """This method is called when the button is clicked"""
    my_teams = anvil.server.call('my_teams',self.user['email'])
    if len(my_teams)==0:
      alert("You haven't saved a team yet")
    else:
      open_form('ShowTeams',my_teams)
    return    

  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    pass





