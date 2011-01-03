#-*- coding: utf-8 -*-
"""This is the authentication system of Stalker. Uses Beaker for the session
management.

This helper module is written to help users to persist their login information
in their system. The aim of this function is not security. So one can quickly
by-pass this system and get himself/herself logged in or query information from
the database without login.

The user information is going to be used in the database to store who created,
updated, read or delete the data.

There are two functions to log a user in, first one is
:func:`~stalker.db.auth.authenticate`, which accepts username and password and
returns a :class:`~stalker.models.user.User` object::
    
    from stalker.db import auth
    userObj = auth.authenticate('username', 'password')

The second one is the :func:`~stalker.db.auth.login` which uses a given
:class:`~stalker.models.user.User` object and creates a Beaker Session and
stores the logged in user id in that session.

The :func:`~stalker.db.auth.get_user` can be used to get the authenticated and
logged in :class:`~stalker.models.user.User` object.

The basic usage of the system is as follows::
    
    from stalker import db
    from stalker.db import auth
    from stalker.models import user
    
    # directly get the user from the database if there is a user_id
    # in the current auth.SESSION
    # 
    # in this way we prevent asking the user for login information all the time
    if 'user_id' in auth.SESSION:
        userObj = auth.get_user()
    else:
        # ask the username and password of the user
        # then authenticate the given user
        username, password = the_interface_for_login()
        userObj = auth.authenticate(username, password)
    
    # login with the given user.User object, this will also create the session
    # if there is no one defined
    auth.login(userObj)


"""

import os
import tempfile
import datetime
from beaker import session as beakerSession
from stalker import db
from stalker.models import error, user



SESSION = {}
SESSION_KEY = 'stalker_key'
SESSION_VALIDATE_KEY = 'stalker_validate_key'



#----------------------------------------------------------------------
def create_session():
    """creates the session
    """
    
    tempdir = tempfile.gettempdir()
    
    session_options = {
        'id': '0',
        'type': 'file',
        'cookie_expires': False,
        'data_dir': os.path.sep.join([tempdir, 'stalker_cache', 'data']),
        'lock_dir': os.path.sep.join([tempdir, 'stalker_cache', 'lock']),
        'key': SESSION_KEY,
        'validate_key': SESSION_VALIDATE_KEY,
    }
    
    SESSION = beakerSession.Session({}, **session_options)
    SESSION.save()



#----------------------------------------------------------------------
def authenticate(username='', password=''):
    """Authenticates the given username and password, returns a
    stalker.models.user.User object
    
    There needs to be a already setup database for the authentication to hapen.
    """
    
    # check if the database is setup
    if db.meta.session == None:
        raise(error.LoginError("stalker is not connected to any db right now, \
use stalker.db.setup(), to setup the default db"))
    
    # try to get the given user
    userObj = db.meta.session.query(user.User).filter_by(name=username).first()
    
    #assert(isinstance(userObj, user.User))
    
    error_msg = "user name and login don't match"
    
    if userObj is None:
        raise(error.LoginError(error_msg))
    
    if userObj.password != password:
        raise(error.LoginError(error_msg))
    
    return userObj



#----------------------------------------------------------------------
def login(user_obj):
    """Persist a user id in the session. This way a user doesn't have to
    reauthenticate on every request
    """
    
    user_obj.last_login = datetime.datetime.now()
    db.meta.session.commit()
    
    if 'user_id' not in SESSION:
        # create the session first
        create_session()
    
    SESSION.update({'user_id': user_obj.id})
    SESSION.save()



#----------------------------------------------------------------------
def logout():
    """removes the current session
    """
    
    assert(isinstance(SESSION, beakerSession.Session))
    
    SESSION.delete()
    SESSION = {}



#----------------------------------------------------------------------
def get_user():
    """returns the user from stored session
    """
    
    # check if the database is setup
    if db.meta.session == None:
        raise(error.LoginError("stalker is not connected to any db right now, \
use stalker.db.setup(), to setup the default db"))
    
    # create the session dictionary
    create_session()
    
    if 'user_id' in SESSION:
        # create the session
        return db.meta.session.query(user.User).\
               filter_by(id=SESSION['user_id']).first()
    else:
        return None
