from . import *  # noqa
from functools import partial


def django_magnificent_messages(request):
    """
    Pass all messages and notifications into context
    """
    return {
        "dmm": {
            'notifications': {
                'all': notifications.get(request),
                'count': notifications.count(request),
            },
            'messages': {
                'all': partial(messages.all, request),
                'all_count': partial(messages.all_count, request),
                'read': partial(messages.read, request),
                'read_count': partial(messages.read_count, request),
                'unread': partial(messages.unread, request),
                'unread_count': partial(messages.unread_count, request),
                'archived': partial(messages.archived, request),
                'archived_count': partial(messages.archived_count, request),
                'sent': partial(messages.sent, request),
                'sent_count': partial(messages.sent_count, request),
                'new': partial(messages.new, request),
                'new_count': partial(messages.new_count, request),
            }
        }
    }
