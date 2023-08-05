from typing import Iterable, Callable

from django.core.paginator import Paginator, Page
from django.utils.safestring import mark_safe

from django_magnificent_messages.storage.base import BaseStorage, Message


class MessageError(Exception):
    MESSAGE_TEMPLATE = ""

    def __init__(self, message_pk):
        self.message_pk = message_pk

    def __str__(self):
        return self.MESSAGE_TEMPLATE.format(message_pk=self.message_pk)


class MessageNotFoundError(MessageError):
    MESSAGE_TEMPLATE = "Message not found in storage for pk `{message_pk}`"


class MultipleMessagesFoundError(MessageError):
    MESSAGE_TEMPLATE = "Multiple messages found in storage for pk `{message_pk}`"


class OperationNotSupprotedError(Exception):
    pass


class StoredMessage(Message):
    def __init__(self,
                 level: int,
                 text: str,
                 subject: str = None,
                 extra=None,
                 html_safe: bool = False,
                 **kwargs):
        if html_safe:
            super().__init__(level, mark_safe(text), subject, extra)
        else:
            super().__init__(level, text, subject, extra)
        for k, v in kwargs.items():
            setattr(self, k, v)


class MessageIterator:
    def __init__(self, stored_messages, convert_function: Callable, fetch_all: bool = True):
        self._stored_messages = stored_messages
        self._convert_function = convert_function
        self._fetch_all = fetch_all
        self._index = 0

    def __iter__(self):
        if self._fetch_all:
            self._stored_messages = list(self._stored_messages)
        self._index = 0
        return self

    def __next__(self):
        try:
            value = self._convert_function(self._stored_messages[self._index])
            self._index += 1
            return value
        except IndexError:
            raise StopIteration()

    def filter(self, *args, **kwargs):
        if hasattr(self._stored_messages, "filter") and callable(self._stored_messages.filter):
            new_stored_messages = self._stored_messages.filter(*args, **kwargs)
            return MessageIterator(new_stored_messages, self._convert_function, self._fetch_all)
        else:
            raise OperationNotSupprotedError("`stored_messages` of type {0} does not support `filter` operation")

    def exclude(self, *args, **kwargs):
        if hasattr(self._stored_messages, "exclude") and callable(self._stored_messages.exclude):
            new_stored_messages = self._stored_messages.exclude(*args, **kwargs)
            return MessageIterator(new_stored_messages, self._convert_function, self._fetch_all)
        else:
            raise OperationNotSupprotedError("`stored_messages` of type {0} does not support `exclude` operation")

    def annotate(self, *args, **kwargs):
        if hasattr(self._stored_messages, "annotate") and callable(self._stored_messages.annotate):
            new_stored_messages = self._stored_messages.annotate(*args, **kwargs)
            return MessageIterator(new_stored_messages, self._convert_function, self._fetch_all)
        else:
            raise OperationNotSupprotedError("`stored_messages` of type {0} does not support `annotate` operation")

    def order_by(self, *args, **kwargs):
        if hasattr(self._stored_messages, "order_by") and callable(self._stored_messages.order_by):
            new_stored_messages = self._stored_messages.order_by(*args, **kwargs)
            return MessageIterator(new_stored_messages, self._convert_function, self._fetch_all)
        else:
            raise OperationNotSupprotedError("`stored_messages` of type {0} does not support `order_by` operation")

    def reverse(self, *args, **kwargs):
        if hasattr(self._stored_messages, "reverse") and callable(self._stored_messages.reverse):
            new_stored_messages = self._stored_messages.reverse(*args, **kwargs)
            return MessageIterator(new_stored_messages, self._convert_function, self._fetch_all)
        else:
            raise OperationNotSupprotedError("`stored_messages` of type {0} does not support `reverse` operation")

    def distinct(self, *args, **kwargs):
        if hasattr(self._stored_messages, "distinct") and callable(self._stored_messages.distinct):
            new_stored_messages = self._stored_messages.distinct(*args, **kwargs)
            return MessageIterator(new_stored_messages, self._convert_function, self._fetch_all)
        else:
            raise OperationNotSupprotedError("`stored_messages` of type {0} does not support `distinct` operation")

    def values(self, *args, **kwargs):
        if hasattr(self._stored_messages, "values") and callable(self._stored_messages.values):
            new_stored_messages = self._stored_messages.values(*args, **kwargs)
            return MessageIterator(new_stored_messages, self._convert_function, self._fetch_all)
        else:
            raise OperationNotSupprotedError("`stored_messages` of type {0} does not support `annotate` operation")

    def values_list(self, *args, **kwargs):
        if hasattr(self._stored_messages, "values_list") and callable(self._stored_messages.values_list):
            new_stored_messages = self._stored_messages.values_list(*args, **kwargs)
            return MessageIterator(new_stored_messages, self._convert_function, self._fetch_all)
        else:
            raise OperationNotSupprotedError("`stored_messages` of type {0} does not support `annotate` operation")

    def dates(self, *args, **kwargs):
        if hasattr(self._stored_messages, "dates") and callable(self._stored_messages.dates):
            new_stored_messages = self._stored_messages.dates(*args, **kwargs)
            return MessageIterator(new_stored_messages, self._convert_function, self._fetch_all)
        else:
            raise OperationNotSupprotedError("`stored_messages` of type {0} does not support `dates` operation")

    def datetimes(self, *args, **kwargs):
        if hasattr(self._stored_messages, "datetimes") and callable(self._stored_messages.datetimes):
            new_stored_messages = self._stored_messages.datetimes(*args, **kwargs)
            return MessageIterator(new_stored_messages, self._convert_function, self._fetch_all)
        else:
            raise OperationNotSupprotedError("`stored_messages` of type {0} does not support `datetimes` operation")

    def select_related(self, *args, **kwargs):
        if hasattr(self._stored_messages, "select_related") and callable(self._stored_messages.select_related):
            new_stored_messages = self._stored_messages.select_related(*args, **kwargs)
            return MessageIterator(new_stored_messages, self._convert_function, self._fetch_all)
        else:
            raise OperationNotSupprotedError("`stored_messages` of type {0} does not support `select_related` "
                                             "operation")

    def prefetch_related(self, *args, **kwargs):
        if hasattr(self._stored_messages, "prefetch_related") and callable(self._stored_messages.prefetch_related):
            new_stored_messages = self._stored_messages.prefetch_related(*args, **kwargs)
            return MessageIterator(new_stored_messages, self._convert_function, self._fetch_all)
        else:
            raise OperationNotSupprotedError("`stored_messages` of type {0} does not support `prefetch_related` "
                                             "operation")

    def defer(self, *args, **kwargs):
        if hasattr(self._stored_messages, "defer") and callable(self._stored_messages.defer):
            new_stored_messages = self._stored_messages.defer(*args, **kwargs)
            return MessageIterator(new_stored_messages, self._convert_function, self._fetch_all)
        else:
            raise OperationNotSupprotedError("`stored_messages` of type {0} does not support `defer` operation")

    def only(self, *args, **kwargs):
        if hasattr(self._stored_messages, "only") and callable(self._stored_messages.only):
            new_stored_messages = self._stored_messages.only(*args, **kwargs)
            return MessageIterator(new_stored_messages, self._convert_function, self._fetch_all)
        else:
            raise OperationNotSupprotedError("`stored_messages` of type {0} does not support `only` operation")

    def using(self, *args, **kwargs):
        if hasattr(self._stored_messages, "using") and callable(self._stored_messages.using):
            new_stored_messages = self._stored_messages.using(*args, **kwargs)
            return MessageIterator(new_stored_messages, self._convert_function, self._fetch_all)
        else:
            raise OperationNotSupprotedError("`stored_messages` of type {0} does not support `using` operation")

    def paginate(self, per_page, orphans=0, allow_empty_first_page=True):
        return MessagePaginator(self._stored_messages, self._convert_function, self._fetch_all, per_page, orphans,
                                allow_empty_first_page)


class MessagePaginator(Paginator):
    def __init__(self, object_list, convert_function, fetch_all, per_page, orphans=0, allow_empty_first_page=True):
        super().__init__(object_list, per_page, orphans, allow_empty_first_page)
        self._convert_function = convert_function
        self._fetch_all = fetch_all

    def _get_page(self, *args, **kwargs):
        """
        Return an instance of a single page.

        This hook can be used by subclasses to use an alternative to the
        standard :cls:`Page` object.
        """
        return MessagePage(self._convert_function, self._fetch_all, *args, **kwargs)


class MessagePage(Page):
    def __init__(self, convert_function, fetch_all, object_list, number, paginator, *args, **kwargs):
        super().__init__(object_list, number, paginator)
        self._convert_function = convert_function
        self._fetch_all = fetch_all

    def __getitem__(self, index):
        return self._convert_function(super(MessagePage, self).__getitem__(index))


class BaseMessageStorage(BaseStorage):
    """
    This is the base message storage.

    We divide messages into following types:
      * All messages
      * Read messages
      * Unread messages
      * Archived messages
      * New messages (messages received since last check)

    Storage should provide methods for getting iterable object of every of this types of messages and methods for
    getting count of messages of each type. This methods wrapped in properties defined in this class.

    Storage should also provide method for saving new message for users or groups.

    **This is not a complete class; to be a usable storage, it must be subclassed and all unimplemented methods
    overridden.**
    """

    ITERATOR_CLASS = MessageIterator

    # Storage API

    def wrap_in_iterator(self, messages):
        return self.ITERATOR_CLASS(messages, self._stored_to_message)

    @property
    def all(self) -> Iterable:
        return self.wrap_in_iterator(self._get_all_messages())

    @property
    def read(self) -> Iterable:
        return self.wrap_in_iterator(self._get_read_messages())

    @property
    def unread(self) -> Iterable:
        return self.wrap_in_iterator(self._get_unread_messages())

    @property
    def archived(self) -> Iterable:
        return self.wrap_in_iterator(self._get_archived_messages())

    @property
    def new(self) -> Iterable:
        return self.wrap_in_iterator(self._get_new_messages())

    @property
    def sent(self) -> Iterable:
        return self.wrap_in_iterator(self._get_sent_messages())

    @property
    def all_count(self) -> int:
        return self._get_all_messages_count()

    @property
    def read_count(self) -> int:
        return self._get_read_messages_count()

    @property
    def unread_count(self) -> int:
        return self._get_unread_messages_count()

    @property
    def archived_count(self) -> int:
        return self._get_archived_messages_count()

    @property
    def new_count(self) -> int:
        return self._get_new_messages_count()

    @property
    def sent_count(self) -> int:
        return self._get_sent_messages_count()

    def get_message(self, message_pk):
        return self._stored_to_message(self._get_message(message_pk))

    def send_message(self,
                     level: int,
                     text: str,
                     subject: str = None,
                     extra: object = None,
                     to_users_pk: Iterable = tuple(),
                     to_groups_pk: Iterable = tuple(),
                     user_generated: bool = True,
                     html_safe: bool = False,
                     reply_to_pk=None) -> StoredMessage:
        """
        Send message.

        Checks message level and that recipient list is not empty. Construct ``Message`` instance and pass it
        into ``_save_message`` method if all checks passed.
        """
        message = self._construct(level, text, subject, extra)
        if message is not None and (to_users_pk or to_groups_pk):
            if user_generated and hasattr(self.request, 'user') and getattr(self.request.user,
                                                                            "is_authenticated", False):
                author_pk = getattr(self.request.user, "pk")
            else:
                author_pk = None

            return self._save_message(message, author_pk=author_pk, to_users_pk=to_users_pk, to_groups_pk=to_groups_pk,
                                      user_generated=user_generated, reply_to_pk=reply_to_pk, html_safe=html_safe)

    def mark_read(self, message_pk):
        self._mark_read(message_pk)

    def mark_unread(self, message_pk):
        self._mark_unread(message_pk)

    def archive(self, message_pk):
        self._archive(message_pk)

    def unarchive(self, message_pk):
        self._unarchive(message_pk)

    # Storage internal methods to implement in subclass

    def _get_all_messages(self) -> Iterable:
        """This method must be implemented by a subclass."""
        raise NotImplementedError('subclasses of BaseMessageStorage must provide a _get_all_messages() method')

    def _get_read_messages(self) -> Iterable:
        """This method must be implemented by a subclass."""
        raise NotImplementedError('subclasses of BaseMessageStorage must provide a _get_read_messages() method')

    def _get_unread_messages(self) -> Iterable:
        """This method must be implemented by a subclass."""
        raise NotImplementedError('subclasses of BaseMessageStorage must provide a _get_unread_messages() method')

    def _get_archived_messages(self) -> Iterable:
        """This method must be implemented by a subclass."""
        raise NotImplementedError(
            'subclasses of BaseMessageStorage must provide a _get_archived_messages() method'
        )

    def _get_new_messages(self) -> Iterable:
        """This method must be implemented by a subclass."""
        raise NotImplementedError('subclasses of BaseMessageStorage must provide a _get_new_messages() method')

    def _get_sent_messages(self) -> Iterable:
        """This method must be implemented by a subclass."""
        raise NotImplementedError('subclasses of BaseMessageStorage must provide a _get_sent_messages() method')

    def _get_all_messages_count(self) -> int:
        """This method must be implemented by a subclass."""
        raise NotImplementedError('subclasses of BaseMessageStorage must provide a _get_all_messages_count() method')

    def _get_read_messages_count(self) -> int:
        """This method must be implemented by a subclass."""
        raise NotImplementedError('subclasses of BaseMessageStorage must provide a _get_read_messages_count() method')

    def _get_unread_messages_count(self) -> int:
        """This method must be implemented by a subclass."""
        raise NotImplementedError('subclasses of BaseMessageStorage must provide a _get_unread_messages_count() method')

    def _get_archived_messages_count(self) -> int:
        """This method must be implemented by a subclass."""
        raise NotImplementedError(
            'subclasses of BaseMessageStorage must provide a _get_archived_messages_count() method'
        )

    def _get_new_messages_count(self) -> int:
        """This method must be implemented by a subclass."""
        raise NotImplementedError('subclasses of BaseMessageStorage must provide a _get_new_messages_count() method')

    def _get_sent_messages_count(self) -> int:
        """This method must be implemented by a subclass."""
        raise NotImplementedError('subclasses of BaseMessageStorage must provide a _get_sent_messages_count() method')

    def _save_message(self,
                      message: Message,
                      author_pk,
                      to_users_pk: Iterable,
                      to_groups_pk: Iterable,
                      user_generated: bool = True,
                      html_safe: bool = False,
                      reply_to_pk=None) -> StoredMessage:
        """This method must be implemented by a subclass."""
        raise NotImplementedError('subclasses of BaseMessageStorage must provide a _save_message() method')

    def _stored_to_message(self, stored) -> StoredMessage:
        """
        Convert message from internal storage representation to StoredMessage instance

        This method must be implemented by a subclass.
        """
        raise NotImplementedError('subclasses of BaseMessageStorage must provide a _stored_to_message() method')

    def _mark_read(self, message_pk):
        raise NotImplementedError('subclasses of BaseMessageStorage must provide a _mark_read() method')

    def _mark_unread(self, message_pk):
        raise NotImplementedError('subclasses of BaseMessageStorage must provide a _mark_unread() method')

    def _archive(self, message_pk):
        raise NotImplementedError('subclasses of BaseMessageStorage must provide a _archive() method')

    def _unarchive(self, message_pk):
        raise NotImplementedError('subclasses of BaseMessageStorage must provide a _unarchive() method')

    def _get_message(self, message_pk):
        raise NotImplementedError('subclasses of BaseMessageStorage must provide a _get_message() method')

    def update_last_checked(self):
        raise NotImplementedError('subclasses of BaseMessageStorage must provide a update_last_checked method')
