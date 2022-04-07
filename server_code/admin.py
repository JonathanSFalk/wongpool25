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
import anvil.pdf
import bcrypt
import stripe 
import json

@anvil.server.callable
def teamlist():
  z = app_tables.teams.search()
  rtn = []
  for t in z:
    print(t['Owner'])
    e = app_tables.users.search(owner=t['Owner'])
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

@anvil.server.http_endpoint("/create-checkout-session")
def create_checkout_session():
  stripe.api_key = anvil.secrets.get_secret('stripe-test-key')
  session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
      'price_data': {
        'currency': 'usd',
        'product_data': {
          'name': 'T-shirt',
        },
        'unit_amount': 2000,
      },
      'quantity': 1,
    }],
    mode='payment',
    success_url='https://wongpool.anvil.app/success',
    cancel_url='https://wongpool.anvil.app/cancel',
  )

  
  return json.dumps(session.id)


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
def _send_email_confirm_link(email):
  """Send an email confirmation link if the specified user's email is not yet confirmed"""
  user = app_tables.users.get(email=email)
  if user is not None and not user['confirmed_email']:
    if user['link_key'] is None:
      user['link_key'] = mk_token()
    anvil.email.send(to=user['email'], subject="Confirm your email address", text=f"""
Hi,

Thanks for signing up for our service. To complete your sign-up, click here to confirm your email address:

{anvil.server.get_app_origin('published')}#?email={url_encode(user['email'])}&confirm={url_encode(user['link_key'])}

Thanks!
""")
    return True
  
@anvil.server.callable
def _do_signup(email, name, password):
  if name is None or name.strip() == "":
    return "Must supply a name"
  if app_tables.users.get(owner=name) is not None:
    return "Name is already being used.  Choose another."
  
  pwhash = hash_password(password, bcrypt.gensalt())
  
  # Add the user in a transaction, to make sure there is only ever one user in this database
  # with this email address. The transaction might retry or abort, so wait until after it's
  # done before sending the email.

  @tables.in_transaction
  def add_user_if_missing():
      
    user = app_tables.users.get(email=email)
    if user is None:
      user = app_tables.users.add_row(email=email, enabled=True, owner=name, password_hash=pwhash)
      return user
    
  user = add_user_if_missing()

  if user is None:
    return "This email address has already been registered for our service. Try logging in."
  
#  _send_email_confirm_link(email)
  
  # No error = success
  anvil.users.force_login(user)
  return None
