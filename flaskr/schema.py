days_of_the_week = [
  'sunday',
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday'
]

pill_schema = ['name', 'description', 'icon']

# attempt to create 30min time slots daily
pillbox_day_template = [
  [] for i in range(24)
]

# 7 arrays for 7 days of the week
pillbox_template = [
  [] for i in range(7)
]
def crreate_pillbox():
  return pillbox_template

def create_pill(name, icon, description):
  pill = {
    'name': name,
    'icon': icon,
    'description': description
  }
  return pill

def create_pill_collection(time, pills):
  collection = {
    'time': time,
    'pills': pills
  }
  return collection

def create_new_user(username, password):
  user = {}
  user['username'] = username
  user['password'] = password
  user['pillbox'] = pillbox_template
  return user
