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

@anvil.server.callable
def export_table_to_json(tname):
  table = app_tables[tname]
  rows = table.search()
  data = []
  for row in rows:
    row_data = dict(row)
    for key, value in row_data.items():
      if isinstance(value, datetime.date):
        row_data[key] = value.strftime('%Y-%m-%d')  # Convert date to date format
      elif isinstance(value, datetime.datetime):
        row_data[key] = value.strftime('%Y-%m-%d %H:%M:%S')  # Convert datetime to string
    data.append(row_data)
  json_data = json.dumps(data)
  json_data_bytes = json_data.encode('utf-8')
  media_object = anvil.BlobMedia("application/json", json_data_bytes, name=tname)
  return media_object

@anvil.server.callable
def import_table(file):
  json_data = file.get_bytes().decode('utf-8')
  data = json.loads(json_data)
  table = app_tables[tname]
  table.delete_all_rows() 
  for row_data in data:
    for key, value in row_data.items():
      if value is not None and key in ['Patient_DOB', 'Date']:
        try:
          parsed_value = datetime.datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
          parsed_value = None
        row_data[key] = parsed_value
      if value is not None and key in ['Timestamp']:
        try:
          parsed_value = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
          parsed_value = None 
        row_data[key] = parsed_value
    table.add_row(**row_data)
  return "Data imported successfully"# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#
