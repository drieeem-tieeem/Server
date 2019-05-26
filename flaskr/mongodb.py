from pymongo import MongoClient 

import click
from flask import current_app, g
from flask.cli import with_appcontext

from flaskr.schema import pillbox_template


def get_db():
  if 'mongodb' not in g:
    client = MongoClient() 
    client = MongoClient('localhost', 27017) 
    g.mongodb = client['drieeem_tieeem'] 
  return g.mongodb

def get_users():
  db = get_db()
  return db['users']

def close_db():
  return

def init_db():
  db = get_db()
  for collection in db.list_collections():
    collection.drop()

@click.command('init-db')
@with_appcontext
def init_db_command():
  """Clear the existing data and create new tables."""
  init_db()
  click.echo('Initialized the database.')
    
def init_app(app):
  app.teardown_appcontext(close_db)
  app.cli.add_command(init_db_command)