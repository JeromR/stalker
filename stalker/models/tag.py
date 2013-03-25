# -*- coding: utf-8 -*-
# Copyright (c) 2009-2013, Erkan Ozgur Yilmaz
# 
# This module is part of Stalker and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

from sqlalchemy import Column, Integer, ForeignKey
from stalker.models.entity import SimpleEntity

from stalker.log import logging_level
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging_level)

class Tag(SimpleEntity):
    """Use it to create tags for any object available in SOM.
    
    Doesn't have any other attribute than what is inherited from
    :class:`~stalker.models.entity.SimpleEntity`
    """
    __auto_name__ = False
    __tablename__ = "Tags"
    __mapper_args__ = {"polymorphic_identity": "Tag"}
    tag_id = Column("id", Integer, ForeignKey("SimpleEntities.id"),
                    primary_key=True)

    def __init__(self, **kwargs):
        super(Tag, self).__init__(**kwargs)

    def __eq__(self, other):
        """the equality operator
        """
        return super(Tag, self).__eq__(other) and isinstance(other, Tag)

    def __ne__(self, other):
        """the inequality operator
        """
        return not self.__eq__(other)
