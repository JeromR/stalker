# -*- coding: utf-8 -*-
# Copyright (c) 2009-2013, Erkan Ozgur Yilmaz
# 
# This module is part of Stalker and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid, forget, remember
from pyramid.view import view_config, forbidden_view_config
from sqlalchemy import or_

import stalker
from stalker import User, Department, Group, Tag, Project
from stalker.db import DBSession
from stalker.views import log_param

import logging
from stalker import log
logger = logging.getLogger(__name__)
logger.setLevel(log.logging_level)

@view_config(
    route_name='add_user',
    renderer='templates/auth/add_user.jinja2',
    permission='Add_User'
)
def add_user(request):
    """called when adding a User
    """
    login = authenticated_userid(request)
    logged_user = User.query.filter_by(login=login).first()
    
    if 'submitted' in request.params:
        logger.debug('submitted in params')
        if request.params['submitted'] == 'add':
            logger.debug('submitted value is: add')
            # create and add a new user
            if 'name' in request.params and \
               'login' in request.params and \
               'email' in request.params and \
               'password' in request.params:
                
                # Departments
                departments = []
                if 'department_ids' in request.params:
                    dep_ids = [
                        int(dep_id)
                        for dep_id in request.POST.getall('department_ids')
                    ]
                    departments = Department.query.filter(
                                    Department.id.in_(dep_ids)).all()
                
                # Groups
                groups = []
                if 'group_ids' in request.params:
                    grp_ids = [
                        int(grp_id)
                        for grp_id in request.POST.getall('group_ids')
                    ]
                    groups = Group.query.filter(
                                    Group.id.in_(grp_ids)).all()
                
                # Tags
                tags = []
                if 'tag_ids' in request.params:
                    tag_ids = [
                        int(tag_id)
                        for tag_id in request.POST.getall('tag_ids')
                    ]
                    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
                
                logger.debug('creating new user')
                new_user = User(
                    name=request.params['name'],
                    login=request.params['login'],
                    email=request.params['email'],
                    password=request.params['password'],
                    created_by=logged_user,
                    departments=departments,
                    groups=groups,
                    tags=tags
                )
                
                logger.debug('adding new user to db')
                DBSession.add(new_user)
                logger.debug('added new user successfully')
            else:
                logger.debug('not all parameters are in request.params')
                log_param(request, 'name')
                log_param(request, 'login')
                log_param(request, 'email')
                log_param(request, 'password')
                
        #elif request.params['submitted'] == 'edit':
        #    # just edit the given user
        #    user_id = request.matchdict['user_id']
        #    user = User.query.filter_by(id=user_id).one()
        #    
        #    with transaction.manager:
        #        user.name = request.params['name']
        #        user.email = request.params['email']
        #        user.password = request.params['password']
        #        user.updated_by = logged_user
        #        # TODO: update the rest later
        #        DBSession.add(user)
        else:
            logger.debug('submitted value is not add but: %s' %
                         request.params['submitted'])
    else:
        logger.debug('submitted is not among parameters')
        for key in request.params.keys():
            logger.debug('request.params[%s]: %s' % (key, request.params[key]))
    
    return {
        'user': logged_user,
    }


@view_config(
    route_name='edit_user',
    renderer='templates/auth/edit_user.jinja2',
    permission='Edit_User'
)
def edit_user(request):
    """called when editing a user
    """
    pass


@view_config(
    route_name='get_users',
    renderer='json',
    permission='View_User'
)
def get_users(request):
    """returns all the users in database
    """
    return [
        {'id': user.id, 'name': user.name}
        for user in User.query.all()
    ]


@view_config(
    route_name='add_group',
    renderer='templates/auth/add_groups.jinja2',
    permission='Add_Group'
)
def add_group(request):
    """runs when adding a new Group
    """
    return {}


@view_config(
    route_name='summarize_user',
    renderer='templates/auth/summarize_user.jinja2'
)
@view_config(
    route_name='view_user_tasks',
    renderer='templates/task/view_tasks.jinja2'
)
def summarize_user(request):
    """runs when getting general User info
    """
    # get the user id
    user_id = request.matchdict['user_id']
    user = User.query.filter_by(id=user_id).first()
    
    return {
        'user': user
    }


@view_config(
    route_name='view_user',
    renderer='templates/auth/view_user.jinja2'
)
def view_user(request):
    
    user_id = request.matchdict['user_id']
    user = User.query.filter_by(id=user_id).first()
    
    return {
        'user': user
    }


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(
        location=request.route_url('login'),
        headers=headers
    )


@view_config(
    route_name='login',
    renderer='templates/auth/login.jinja2'
)
def login(request):
    """the login view
    """
    logger.debug('login start')
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/'

    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''

    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']

        # need to find the user
        # check with the login or email attribute
        user_obj = User.query\
            .filter(or_(User.login==login, User.email==login)).first()

        if user_obj:
            login = user_obj.login

        if user_obj and user_obj.check_password(password):
            headers = remember(request, login)
            return HTTPFound(
                location=came_from,
                headers=headers,
            )

        message = 'Wrong username or password!!!'

    logger.debug('login end')
    return dict(
        message=message,
        url=request.application_url + '/login',
        came_from=came_from,
        login=login,
        password=password,
        stalker=stalker
    )


@forbidden_view_config(
    renderer='templates/auth/no_permission.jinja2'
)
def forbidden(request):
    """runs when user has no permission for the requested page
    """
    return {}


@view_config(route_name='home',
            renderer='templates/base.jinja2')
@view_config(route_name='me_menu',
             renderer='templates/auth/me_menu.jinja2')
def home(request):
    login = authenticated_userid(request)
    user = User.query.filter_by(login=login).first()
    projects = Project.query.all()
    return {
        'stalker': stalker,
        'user': user,
        'projects': projects,
    }
