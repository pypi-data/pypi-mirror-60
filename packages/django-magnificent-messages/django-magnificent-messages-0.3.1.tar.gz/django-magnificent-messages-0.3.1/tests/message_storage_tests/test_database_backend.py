from django.urls import reverse

from django_magnificent_messages.models import MessageNotSentToUserError
from django_magnificent_messages.storage.message_storage.db import DatabaseStorage
from tests.message_storage_tests.base import BaseMessageStorageTestCases


class DatabaseStorageExistingTestCase(BaseMessageStorageTestCases.ExistingMessagesTestCase):
    STORAGE = DatabaseStorage

    def test_anonymous_api(self):
        """API should always return 0 messages for anonymous user"""
        show_url = reverse('messages_show', args=(1,))
        response = self.client.get(show_url)
        self.assertIn('dmm', response.context)
        # Counts passed in context as functions to avoid SQL-query execution until last moment. So in tests this
        # context variables should be executed
        self.assertEqual(0, response.context['dmm']['messages']['all_count']())
        self.assertEqual(0, response.context['dmm']['messages']['read_count']())
        self.assertEqual(0, response.context['dmm']['messages']['unread_count']())
        self.assertEqual(0, response.context['dmm']['messages']['archived_count']())
        self.assertEqual(0, response.context['dmm']['messages']['new_count']())
        self.assertEqual([], list(response.context['dmm']["messages"]["new"]()))
        self.assertEqual([], list(response.context['dmm']["messages"]["all"]()))
        self.assertEqual([], list(response.context['dmm']["messages"]["read"]()))
        self.assertEqual([], list(response.context['dmm']["messages"]["unread"]()))
        self.assertEqual([], list(response.context['dmm']["messages"]["archived"]()))

    def test_mark_read_self(self):
        self.bob_storage.mark_read(self.alice_message_to_bob.pk)
        messages = list(self.bob_storage.read)
        self.assertIn(self.alice_message_to_bob, messages)

    def test_mark_read_group_self(self):
        self.alice_storage.mark_read(self.bob_message_to_group1.pk)
        messages = list(self.alice_storage.read)
        self.assertIn(self.bob_message_to_group1, messages)
        self.assertNotIn(self.bob_message_to_group1, list(self.bob_storage.read))

    def test_mark_read_other(self):
        with self.assertRaisesMessage(MessageNotSentToUserError,
                                      "<Message: 1> was not sent to user, who tried to mark it as read"):
            self.carol_storage.mark_read(self.alice_message_to_bob.pk)

    def test_mark_unread_self(self):
        self.bob_storage.mark_unread(self.read_message.pk)
        messages = list(self.bob_storage.unread)
        self.assertIn(self.read_message, messages)

    def test_mark_unread_group_self(self):
        self.alice_storage.mark_unread(self.read_message.pk)
        messages = list(self.alice_storage.unread)
        self.assertIn(self.read_message, messages)
        self.assertNotIn(self.read_message, list(self.bob_storage.unread))

    def test_mark_unread_other(self):
        with self.assertRaisesMessage(MessageNotSentToUserError,
                                      "<Message: 3> was not sent to user, who tried to mark it as read"):
            self.carol_storage.mark_read(self.read_message.pk)

    def test_archive_self(self):
        self.bob_storage.archive(self.alice_message_to_bob.pk)
        messages = list(self.bob_storage.archived)
        self.assertIn(self.alice_message_to_bob, messages)

    def test_archive_group_self(self):
        self.alice_storage.archive(self.bob_message_to_group1.pk)
        messages = list(self.alice_storage.archived)
        self.assertIn(self.bob_message_to_group1, messages)
        self.assertNotIn(self.bob_message_to_group1, list(self.bob_storage.archived))

    def test_archive_other(self):
        with self.assertRaisesMessage(MessageNotSentToUserError,
                                      "<Message: 1> was not sent to user, who tried to archive it"):
            self.carol_storage.archive(self.alice_message_to_bob.pk)

    def test_unarchive_self(self):
        self.bob_storage.unarchive(self.archived_message.pk)
        messages = list(self.bob_storage.all)
        self.assertIn(self.archived_message, messages)

    def test_unarchive_group_self(self):
        self.alice_storage.unarchive(self.archived_message.pk)
        messages = list(self.alice_storage.all)
        self.assertIn(self.archived_message, messages)
        self.assertNotIn(self.archived_message, list(self.bob_storage.all))

    def test_unarchive_other(self):
        with self.assertRaisesMessage(MessageNotSentToUserError,
                                      "<Message: 4> was not sent to user, who tried to archive it"):
            self.carol_storage.archive(self.archived_message.pk)


class DatabaseStorageClearTestCase(BaseMessageStorageTestCases.ClearTestCase):
    STORAGE = DatabaseStorage
