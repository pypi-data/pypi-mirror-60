# -*- coding: utf-8 -*-
from plone.uuid.interfaces import IUUID


def getUID(context):
    uid = IUUID(context, None)  # noqa: P001
    if uid is not None:
        return uid

    if hasattr(context, 'UID'):  # noqa: P002
        return context.UID()

    try:
        return '/'.join(context.getPhysicalPath())
    except AttributeError:
        pass

    try:
        return context.id
    except AttributeError:
        return ''
