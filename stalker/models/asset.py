# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of Stalker and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import reconstructor
from stalker.models.entity import TaskableEntity
from stalker.models.mixins import StatusMixin, ReferenceMixin

class Asset(TaskableEntity, ReferenceMixin, StatusMixin):
    """The Asset class is the whole idea behind Stalker.
    
    *Assets* are containers of :class:`~stalker.models.task.Task`\ s. And
    :class:`~stalker.models.task.Task`\ s are the smallest meaningful part that
    should be accomplished to complete the
    :class:`~stalker.models.project.Project`.
    
    An example could be given as follows; you can create an asset for one of
    the characters in your project. Than you can divide this character asset in
    to :class:`~stalker.models.task.Task`\ s. These
    :class:`~stalker.models.task.Task`\ s can be defined by the type of the
    :class:`~stalker.models.asset.Asset`, which is a
    :class:`~stalker.models.type.Type` object created specifically for
    :class:`~stalker.models.asset.Asset` (ie. has its
    :attr:`~stalker.models.type.Type.target_entity_type` set to "Asset"),
    
    An :class:`~stalker.models.asset.Asset` instance should be initialized with
    a :class:`~stalker.models.project.Project` instance (as the other classes
    which are mixed with the :class:`~stalker.models.mixins.TaskMixin`). And
    when a :class:`~stalker.models.project.Project` instance is given then the
    asset will append itself to the
    :attr:`~stalker.models.project.Project.assets` list.
    
    ..versionadded: 0.2.0:
        No more Asset to Shot connection:
        
        Assets now are not directly related to Shots. Instead a
        :class:`~stalker.models.Version` will reference the Asset and then it
        is easy to track which shots are referencing this Asset by querying
        with a join of Shot Versions referencing this Asset.
    """

    __strictly_typed__ = True
    __tablename__ = "Assets"
    __mapper_args__ = {"polymorphic_identity": "Asset"}

    asset_id = Column("id", Integer, ForeignKey("TaskableEntities.id"),
                      primary_key=True)


    def __init__(self, **kwargs):
        super(Asset, self).__init__(**kwargs)

        # call the mixin init methods
        ReferenceMixin.__init__(self, **kwargs)
        StatusMixin.__init__(self, **kwargs)

    @reconstructor
    def __init_on_load__(self):
        """initialized the instance variables when the instance created with
        SQLAlchemy
        """
        # call supers __init_on_load__
        super(Asset, self).__init_on_load__()


    def __eq__(self, other):
        """the equality operator
        """
        return super(Asset, self).__eq__(other) and\
               isinstance(other, Asset) and self.type == other.type