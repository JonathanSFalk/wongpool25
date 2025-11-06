from ._anvil_designer import TeamColumnTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class TeamColumn(TeamColumnTemplate):
  def __init__(self, teamrow, print_switch, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    if print_switch:
      self.delete_btn.visible = False
      self.rename_btn.visible = False
    self.teamrow = teamrow
    _,p,_,_ = anvil.server.call('pdict')
    p = {int(k):v for k,v in p.items()}
    # Any code you write here will run when the form opens.
    self.name_lbl.text = teamrow['Teamname']
    self.p1_lbl.text = p[teamrow['P1']]
    self.p2_lbl.text = p[teamrow['P2']]
    self.p3_lbl.text = p[teamrow['P3']]
    self.p4_lbl.text = p[teamrow['P4']]
    self.p5_lbl.text = p[teamrow['P5']]
    self.p6_lbl.text = p[teamrow['P6']]
    self.p7_lbl.text = p[teamrow['P7']]
    self.p8_lbl.text = p[teamrow['P8']]
    
   
  def rename_btn_click(self, **event_args):
      teamname = self.name_lbl.text
      t = TextBox(placeholder="Enter New Team Name Here")
      named = False
      while not named:
        name = alert(content=t,title="Change " + teamname, dismissible=False)
        if not name or not t.text or t.text==teamname:
          n = Notification('Name Unchanged')
          n.show()
          return named
        else:          
          named = anvil.server.call('name_check',t.text)
          if not named:
            n = Notification('Name already used. Try Another.',timeout=3)
            n.show()
            time.sleep(4)
      newname = anvil.server.call('update_team',teamname,0,t.text)
      my_teams = anvil.server.call('my_teams',anvil.users.get_user()['email'])
      open_form('ShowTeams',my_teams)


  def delete_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    teamname = self.name_lbl.text
    go_ahead = alert('Permanently delete your team: ' + teamname ,buttons=[('Yes',1),('No',0)],dismissible=False)
    if go_ahead:
      success = anvil.server.call('update_team',teamname,1)
    else:
      n=Notification('Delete Cancelled')
      n.show
    my_teams = anvil.server.call('my_teams',anvil.users.get_user()['email'])  
    open_form('ShowTeams',my_teams)




  
