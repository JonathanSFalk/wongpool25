import anvil.facebook.auth
import stripe.checkout
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

__user = None
__mstands = None
__cstands = None
__tstands = None
__retmat = None
__hothomers = None
__lupdate = None

def stands():
  global __mstands, __cstands, __tstands
  if __mstands:
    return __mstands,__cstands,__tstands
  __mstands, __cstands, __tstands = anvil.server.call('index')
  return __mstands, __cstands, __tstands

def get_p2team():
  global __retmat
  if __retmat:
    return __retmat
  __retmat = anvil.server.call('p2team')
  return __retmat

def get_hothomers():
  global __hothomers
  if __hothomers:
    return __hothomers
  __hothomers = anvil.server.call('hothomers')
  return __hothomers

def get_lupdate():
  global __lupdate
  if __lupdate:
    return __lupdate
  __lupdate = anvil.server.call('lupdate')
  return __lupdate