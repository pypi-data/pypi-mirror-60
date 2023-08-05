import json

from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.test import TestCase, RequestFactory, override_settings
from django.urls import reverse

from django_magnificent_messages import constants, models
from django_magnificent_messages.models import Message
from django_magnificent_messages.storage.message_storage.base import StoredMessage
from tests.utils import TestMessagesMixin


class TestStoragesMixin:
    def create_test_storages(self):
        r = self.rf.get("/")
        r.user = self.alice
        self.alice_storage = self.STORAGE(r)

        r = self.rf.get("/")
        r.user = self.bob
        self.bob_storage = self.STORAGE(r)

        r = self.rf.get("/")
        r.user = self.carol
        self.carol_storage = self.STORAGE(r)

        r = self.rf.get("/")
        r.user = AnonymousUser()
        self.anonymous_storage = self.STORAGE(r)


class BaseMessageStorageTestCases:
    class ClearTestCase(TestMessagesMixin, TestStoragesMixin, TestCase):
        STORAGE = None

        def setUp(self) -> None:
            self.create_test_users()
            self.rf = RequestFactory()
            self.create_test_storages()

        def test_send_to_user(self):
            self.alice_storage.send_message(constants.INFO, "Hi, Bob!", to_users_pk=[self.bob.pk], user_generated=True)
            self.assertEqual(1, models.Message.objects.count())
            message = models.Message.objects.all()[0]
            self.assertEqual(constants.INFO, message.level)
            self.assertEqual("Hi, Bob!", message.text)
            self.assertEqual(self.alice, message.author)
            self.assertIn(self.bob, message.sent_to_users.all())

        def test_send_to_group(self):
            self.alice_storage.send_message(constants.INFO, "Hi, Group!", to_groups_pk=[self.group1.pk, self.group2.pk],
                                            user_generated=True)
            self.assertEqual(1, models.Message.objects.count())
            message = models.Message.objects.all()[0]
            self.assertEqual(constants.INFO, message.level)
            self.assertEqual("Hi, Group!", message.text)
            self.assertEqual(self.alice, message.author)
            self.assertSequenceEqual([self.group1, self.group2], message.sent_to_groups.all())

        def test_anonymous_send_to_user(self):
            self.anonymous_storage.send_message(constants.INFO, "Hi, Bob!", to_users_pk=[self.bob.pk],
                                                user_generated=True)
            self.assertEqual(1, models.Message.objects.count())
            message = models.Message.objects.all()[0]
            self.assertEqual(constants.INFO, message.level)
            self.assertEqual("Hi, Bob!", message.text)
            self.assertEqual(None, message.author)
            self.assertIn(self.bob, message.sent_to_users.all())

        def test_anonymous_send_to_group(self):
            self.anonymous_storage.send_message(constants.INFO, "Hi, Group!",
                                                to_groups_pk=[self.group1.pk, self.group2.pk],
                                                user_generated=True)
            self.assertEqual(1, models.Message.objects.count())
            message = models.Message.objects.all()[0]
            self.assertEqual(constants.INFO, message.level)
            self.assertEqual("Hi, Group!", message.text)
            self.assertEqual(None, message.author)
            self.assertSequenceEqual([self.group1, self.group2], message.sent_to_groups.all())

        def test_convert(self):
            message = Message.objects.create(pk=1, level=constants.INFO, text="Alice message to Bob",
                                             author=self.alice, user_generated=True)
            message.sent_to_users.add(self.bob)

            stored = self.alice_storage._stored_to_message(message)
            self.assertEqual(constants.INFO, stored.level)
            self.assertEqual("Alice message to Bob", stored.text)
            self.assertIsNone(stored.subject)
            self.assertIsNone(stored.extra)
            self.assertEqual(self.alice, stored.author)
            self.assertTrue(stored.user_generated)
            self.assertIsNone(stored.reply_to)

        @override_settings(DMM_MINIMAL_LEVEL=0)
        def test_full_cycle_no_show_new(self):
            """
            With the message middleware enabled, messages are properly stored and
            retrieved across the full request/redirect/response cycle.
            """
            data = {
                "messages": [
                    {
                        'text': 'Test text %d' % x,
                        'to_users_pk': [self.alice.pk]
                    } for x in range(5)],
                'show_new': 0
            }
            show_url = reverse('messages_show', args=(0,))
            for level in ('secondary', 'primary', 'info', 'success', 'warning', 'error'):
                # Clear messages
                models.Message.objects.all().delete()
                add_url = reverse('add-message', args=(level,))
                logged = self.client.login(username='alice', password='password')
                response = self.client.post(add_url, json.dumps(data), follow=True, content_type="application/json")
                self.assertRedirects(response, show_url)
                self.assertIn('dmm', response.context)
                # Counts passed in context as functions to avoid SQL-query execution until last moment. So in tests this
                # context variables should be executed
                self.assertEqual(5, response.context['dmm']['messages']['all_count']())
                self.assertEqual(5, response.context['dmm']['messages']['unread_count']())
                self.assertEqual(5, response.context['dmm']['messages']['new_count']())
                messages = [StoredMessage(constants.DEFAULT_LEVELS[level.upper()],
                                          msg['text'], subject=None, extra=None) for msg in data['messages']]
                messages.reverse()
                self.assertEqual(list(response.context['dmm']['messages']['all']()), messages)

        @override_settings(DMM_MINIMAL_LEVEL=0)
        def test_full_cycle_show_new(self):
            """
            With the message middleware enabled, messages are properly stored and
            retrieved across the full request/redirect/response cycle.
            """
            data = {
                "messages": [
                    {
                        'text': 'Test text %d' % x,
                        'to_users_pk': [self.alice.pk]
                    } for x in range(5)],
                'show_new': 1
            }
            show_url = reverse('messages_show', args=(1,))
            for level in ('secondary', 'primary', 'info', 'success', 'warning', 'error'):
                # Clear messages
                models.Message.objects.all().delete()
                add_url = reverse('add-message', args=(level,))
                logged = self.client.login(username='alice', password='password')
                response = self.client.post(add_url, json.dumps(data), follow=True, content_type="application/json")
                self.assertRedirects(response, show_url)
                self.assertIn('dmm', response.context)
                # Counts passed in context as functions to avoid SQL-query execution until last moment. So in tests this
                # context variables should be executed
                self.assertEqual(5, response.context['dmm']['messages']['all_count']())
                self.assertEqual(5, response.context['dmm']['messages']['unread_count']())
                self.assertEqual(5, response.context['dmm']['messages']['new_count']())
                messages = [StoredMessage(constants.DEFAULT_LEVELS[level.upper()],
                                          msg['text'], subject=None, extra=None) for msg in data['messages']]
                messages.reverse()
                self.assertEqual(list(response.context['dmm']['messages']['all']()), messages)
                for msg in data["messages"]:
                    self.assertContains(response, msg['text'])

        @override_settings(DMM_MINIMAL_LEVEL=0)
        def test_full_cycle_multiple_post_show_new(self):
            show_url = reverse('messages_show', args=(1,))
            logged = self.client.login(username='alice', password='password')
            messages = []
            for level in ('secondary', 'primary', 'info', 'success', 'warning', 'error'):
                for i in range(5):
                    data = {
                        "messages": [
                            {
                                'text': 'Test %s %d' % (level, i),
                                'to_users_pk': [self.alice.pk]
                            }],
                        'show_new': 1
                    }
                    messages.append(StoredMessage(constants.DEFAULT_LEVELS[level.upper()],
                                                  'Test %s %d' % (level, i), subject=None, extra=None))
                    add_url = reverse('add-message', args=(level,))
                    response = self.client.post(add_url, json.dumps(data), content_type="application/json")
            response = self.client.get(show_url)
            self.assertIn('dmm', response.context)
            # Counts passed in context as functions to avoid SQL-query execution until last moment. So in tests this
            # context variables should be executed
            self.assertEqual(len(messages), response.context['dmm']['messages']['all_count']())
            self.assertEqual(len(messages), response.context['dmm']['messages']['unread_count']())
            self.assertEqual(len(messages), response.context['dmm']['messages']['new_count']())
            messages.reverse()
            self.assertEqual(list(response.context['dmm']['messages']['all']()), messages)
            for msg in messages:
                self.assertContains(response, msg.text)

        @override_settings(DMM_MINIMAL_LEVEL=0)
        def test_system_full_cycle_no_show_new(self):
            """
            With the message middleware enabled, messages are properly stored and
            retrieved across the full request/redirect/response cycle.
            """
            data = {
                "messages": [
                    {
                        'text': 'Test text %d' % x,
                        'to_users_pk': [self.alice.pk]
                    } for x in range(5)],
                'show_new': 0
            }
            show_url = reverse('messages_show', args=(0,))
            for level in ('secondary', 'primary', 'info', 'success', 'warning', 'error'):
                # Clear messages
                models.Message.objects.all().delete()
                add_url = reverse('add-system-message', args=(level,))
                logged = self.client.login(username='alice', password='password')
                response = self.client.post(add_url, json.dumps(data), follow=True, content_type="application/json")
                self.assertRedirects(response, show_url)
                self.assertIn('dmm', response.context)
                # Counts passed in context as functions to avoid SQL-query execution until last moment. So in tests this
                # context variables should be executed
                self.assertEqual(5, response.context['dmm']['messages']['all_count']())
                self.assertEqual(5, response.context['dmm']['messages']['unread_count']())
                self.assertEqual(5, response.context['dmm']['messages']['new_count']())
                messages = [StoredMessage(constants.DEFAULT_LEVELS[level.upper()],
                                          msg['text'], subject=None, extra=None) for msg in data['messages']]
                messages.reverse()
                self.assertEqual(list(response.context['dmm']['messages']['all']()), messages)

        @override_settings(DMM_MINIMAL_LEVEL=0)
        def test_system_full_cycle_show_new(self):
            """
            With the message middleware enabled, messages are properly stored and
            retrieved across the full request/redirect/response cycle.
            """
            data = {
                "messages": [
                    {
                        'text': 'Test text %d' % x,
                        'to_users_pk': [self.alice.pk]
                    } for x in range(5)],
                'show_new': 1
            }
            show_url = reverse('messages_show', args=(1,))
            for level in ('secondary', 'primary', 'info', 'success', 'warning', 'error'):
                # Clear messages
                models.Message.objects.all().delete()
                add_url = reverse('add-system-message', args=(level,))
                logged = self.client.login(username='alice', password='password')
                response = self.client.post(add_url, json.dumps(data), follow=True, content_type="application/json")
                self.assertRedirects(response, show_url)
                self.assertIn('dmm', response.context)
                # Counts passed in context as functions to avoid SQL-query execution until last moment. So in tests this
                # context variables should be executed
                self.assertEqual(5, response.context['dmm']['messages']['all_count']())
                self.assertEqual(5, response.context['dmm']['messages']['unread_count']())
                self.assertEqual(5, response.context['dmm']['messages']['new_count']())
                messages = [StoredMessage(constants.DEFAULT_LEVELS[level.upper()],
                                          msg['text'], subject=None, extra=None) for msg in data['messages']]
                messages.reverse()
                self.assertEqual(list(response.context['dmm']['messages']['all']()), messages)
                for msg in data["messages"]:
                    self.assertContains(response, msg['text'])

        @override_settings(DMM_MINIMAL_LEVEL=0)
        def test_system_full_cycle_multiple_post_show_new(self):
            show_url = reverse('messages_show', args=(1,))
            logged = self.client.login(username='alice', password='password')
            messages = []
            for level in ('secondary', 'primary', 'info', 'success', 'warning', 'error'):
                for i in range(5):
                    data = {
                        "messages": [
                            {
                                'text': 'Test %s %d' % (level, i),
                                'to_users_pk': [self.alice.pk]
                            }],
                        'show_new': 1
                    }
                    messages.append(StoredMessage(constants.DEFAULT_LEVELS[level.upper()],
                                                  'Test %s %d' % (level, i), subject=None, extra=None))
                    add_url = reverse('add-system-message', args=(level,))
                    response = self.client.post(add_url, json.dumps(data), content_type="application/json")
            response = self.client.get(show_url)
            self.assertIn('dmm', response.context)
            # Counts passed in context as functions to avoid SQL-query execution until last moment. So in tests this
            # context variables should be executed
            self.assertEqual(len(messages), response.context['dmm']['messages']['all_count']())
            self.assertEqual(len(messages), response.context['dmm']['messages']['unread_count']())
            self.assertEqual(len(messages), response.context['dmm']['messages']['new_count']())
            messages.reverse()
            self.assertEqual(list(response.context['dmm']['messages']['all']()), messages)
            for msg in messages:
                self.assertContains(response, msg.text)

    class ExistingMessagesTestCase(TestMessagesMixin, TestStoragesMixin, TestCase):
        """
        For message testing next situation is used:
            * There are 3 users (Alice, Bob and Carol) and two groups (group1 and group2)
            * Alice is in group1, Bob is in group1 and group2, Carol is not in any group
            * Alice sent message "Alice message to Bob" to Bob
            * Bob sent message "Bob message go group1" to group1
            * Carol sent two messages "Read message" and "Archived message" to alice and group2
            * Bob and Alice marked "Read message" as read
            * Bob and Alice archived "Archived message"

        This is situation with messages at the start of every test.

        All users checked theirs inboxes very long time ago
        """
        STORAGE = None

        def setUp(self) -> None:
            self.create_test_users()
            self.create_test_messages()
            self.rf = RequestFactory()
            self.create_test_storages()
            self.alice_message_to_bob = self.alice_storage._stored_to_message(self.alice_message_to_bob)
            self.bob_message_to_group1 = self.alice_storage._stored_to_message(self.bob_message_to_group1)
            self.read_message = self.alice_storage._stored_to_message(self.read_message)
            self.archived_message = self.alice_storage._stored_to_message(self.archived_message)

        def test_all_count(self):
            """
            Archived messages never counts, so
                * Alice has 2 messages ("Bob message go group1", "Read message")
                * Bob has 3 messages ("Alice message to Bob", "Bob message go group1", "Read message")
                * Carol has 0 messages
                * Anonymous user always has no incoming messages
            """
            self.assertEqual(2, self.alice_storage.all_count)
            self.assertEqual(3, self.bob_storage.all_count)
            self.assertEqual(0, self.carol_storage.all_count)
            self.assertEqual(0, self.anonymous_storage.all_count)

        def test_read_count(self):
            """
            Archived messages never counts, so
                * Alice and Bob have 1 read message ("Read message")
                * Carol has 0 messages
                * Anonymous user always has no incoming messages
            """
            self.assertEqual(1, self.alice_storage.read_count)
            self.assertEqual(1, self.bob_storage.read_count)
            self.assertEqual(0, self.carol_storage.read_count)
            self.assertEqual(0, self.anonymous_storage.read_count)

        def test_unread_count(self):
            """
            Archived messages never counts, so
                * Alice has 1 messages ("Bob message go group1")
                * Bob has 2 messages ("Alice message to Bob", "Bob message go group1")
                * Carol has 0 messages
                * Anonymous user always has no incoming messages
            """
            self.assertEqual(1, self.alice_storage.unread_count)
            self.assertEqual(2, self.bob_storage.unread_count)
            self.assertEqual(0, self.carol_storage.unread_count)
            self.assertEqual(0, self.anonymous_storage.unread_count)

        def test_archived_count(self):
            """
            Bob and Alice have 1 archived message ("Archived message")
            * Anonymous user always has no incoming messages
            """
            self.assertEqual(1, self.alice_storage.archived_count)
            self.assertEqual(1, self.bob_storage.archived_count)
            self.assertEqual(0, self.carol_storage.archived_count)
            self.assertEqual(0, self.anonymous_storage.archived_count)

        def test_new_count(self):
            """
            Archived messages never counts and users never checked their storages, so
                * Alice has 2 messages ("Bob message go group1", "Read message")
                * Bob has 3 messages ("Alice message to Bob", "Bob message go group1", "Read message")
                * Carol has 0 messages
                * Anonymous user always has no incoming messages
            """
            self.assertEqual(2, self.alice_storage.new_count)
            self.assertEqual(3, self.bob_storage.new_count)
            self.assertEqual(0, self.carol_storage.new_count)
            self.assertEqual(0, self.anonymous_storage.new_count)

        def test_sent_count(self):
            """
                * Alice has 1 message ("Alice message to Bob", "Read message")
                * Bob has 1 messages ("Alice message to Bob", "Bob message go group1", "Read message")
                * Carol has 2 messages ("Read message", "Archived message")
                * Anonymous user always has no messages
            """
            self.assertEqual(1, self.alice_storage.sent_count)
            self.assertEqual(1, self.bob_storage.sent_count)
            self.assertEqual(2, self.carol_storage.sent_count)
            self.assertEqual(0, self.anonymous_storage.sent_count)

        def test_alice_all(self):
            """
            Alice has 2 messages - "Bob message go group1", "Read message".
            Archived message should not be here.
            All other messages in system should not be in her storage.
            """
            messages = list(self.alice_storage.all)
            self.assertEqual(2, len(messages))
            self.assertIn(self.bob_message_to_group1, messages)
            self.assertIn(self.read_message, messages)
            self.assertNotIn(self.alice_message_to_bob, messages)
            self.assertNotIn(self.archived_message, messages)

        def test_alice_read(self):
            """
            Alice has 1 read message ("Read message")
            All other messages in system should not be here
            """
            messages = list(self.alice_storage.read)
            self.assertEqual(1, len(messages))
            self.assertNotIn(self.bob_message_to_group1, messages)
            self.assertIn(self.read_message, messages)
            self.assertNotIn(self.alice_message_to_bob, messages)
            self.assertNotIn(self.archived_message, messages)

        def test_alice_unread(self):
            """
            Alice has 1 unread message ("Bob message go group1")
            Archived message should not be here.
            All other messages in system should not be here
            """
            messages = list(self.alice_storage.unread)
            self.assertEqual(1, len(messages))
            self.assertIn(self.bob_message_to_group1, messages)
            self.assertNotIn(self.read_message, messages)
            self.assertNotIn(self.alice_message_to_bob, messages)
            self.assertNotIn(self.archived_message, messages)

        def test_alice_new(self):
            """
            Alice has never checked storage, so all her messages other then "Archived message" should be here.
            """
            messages = list(self.alice_storage.new)
            self.assertEqual(2, len(messages))
            self.assertIn(self.bob_message_to_group1, messages)
            self.assertIn(self.read_message, messages)
            self.assertNotIn(self.alice_message_to_bob, messages)
            self.assertNotIn(self.archived_message, messages)

        def test_alice_sent(self):
            """
            Alice sent one message ("Alice message to Bob").
            """
            messages = list(self.alice_storage.sent)
            self.assertEqual(1, len(messages))
            self.assertIn(self.alice_message_to_bob, messages)

        def test_bob_all(self):
            """
            Bob has 3 messages - "Alice message to Bob", "Bob message go group1", "Read message".
            Archived message should not be here.
            """
            messages = list(self.bob_storage.all)
            self.assertEqual(3, len(messages))
            self.assertIn(self.bob_message_to_group1, messages)
            self.assertIn(self.read_message, messages)
            self.assertIn(self.alice_message_to_bob, messages)
            self.assertNotIn(self.archived_message, messages)

        def test_bob_read(self):
            """
            Bob has 1 read message ("Read message")
            All other messages in system should not be here
            """
            messages = list(self.bob_storage.read)
            self.assertEqual(1, len(messages))
            self.assertNotIn(self.bob_message_to_group1, messages)
            self.assertIn(self.read_message, messages)
            self.assertNotIn(self.alice_message_to_bob, messages)
            self.assertNotIn(self.archived_message, messages)

        def test_bob_unread(self):
            """
            Alice has 2 unread message ("Alice message to Bob", "Bob message go group1")
            Archived message should not be here.
            All other messages in system should not be here
            """
            messages = list(self.bob_storage.unread)
            self.assertEqual(2, len(messages))
            self.assertIn(self.bob_message_to_group1, messages)
            self.assertNotIn(self.read_message, messages)
            self.assertIn(self.alice_message_to_bob, messages)
            self.assertNotIn(self.archived_message, messages)

        def test_bob_new(self):
            """
            Bob has never checked inbox, so all his messages other then "Archived message" should be here.
            """
            messages = list(self.bob_storage.new)
            self.assertEqual(3, len(messages))
            self.assertIn(self.bob_message_to_group1, messages)
            self.assertIn(self.read_message, messages)
            self.assertIn(self.alice_message_to_bob, messages)
            self.assertNotIn(self.archived_message, messages)

        def test_bob_sent(self):
            """
            Bob sent one message ("Bob message to group1").
            """
            messages = list(self.bob_storage.sent)
            self.assertEqual(1, len(messages))
            self.assertIn(self.bob_message_to_group1, messages)

        def test_carol(self):
            """
            Carol has totally empty inbox
            """
            self.assertEqual(0, len(list(self.carol_storage.all)))
            self.assertEqual(0, len(list(self.carol_storage.read)))
            self.assertEqual(0, len(list(self.carol_storage.unread)))
            self.assertEqual(0, len(list(self.carol_storage.archived)))
            self.assertEqual(0, len(list(self.carol_storage.new)))

        def test_carol_sent(self):
            """
            Bob sent one message ("Bob message to group1").
            """
            messages = list(self.carol_storage.sent)
            self.assertEqual(2, len(messages))
            self.assertIn(self.read_message, messages)
            self.assertIn(self.archived_message, messages)

        def test_anonymous(self):
            """
            Anonymous user always has no incoming or outcoming messages
            """
            self.assertEqual(0, len(list(self.anonymous_storage.all)))
            self.assertEqual(0, len(list(self.anonymous_storage.read)))
            self.assertEqual(0, len(list(self.anonymous_storage.unread)))
            self.assertEqual(0, len(list(self.anonymous_storage.archived)))
            self.assertEqual(0, len(list(self.anonymous_storage.new)))
            self.assertEqual(0, len(list(self.anonymous_storage.sent)))

        def test_new_after_check(self):
            """
            new should respect previous checks
            """
            # Emulate check
            self.alice_storage.update_last_checked()

            # Right after check user has no new messages
            self.assertEqual(0, self.alice_storage.new_count)
            self.assertEqual(0, len(list(self.alice_storage.new)))

            # New message
            new_message = Message.objects.create(level=constants.INFO, text="Alice message to Bob",
                                                 author=self.bob, user_generated=True)
            new_message.sent_to_users.add(self.alice)

            # Now user has 1 new message
            self.assertEqual(1, self.alice_storage.new_count)
            new_messages = list(self.alice_storage.new)
            self.assertEqual(1, len(new_messages))

        def test_subsequent_new_messages(self):
            """
            If multiple messages sent to user after his last check, all this messages should be in storage.new
            when user finally checks messages
            """
            # Emulate check
            self.alice_storage.update_last_checked()

            messages = []
            for i in range(5):
                new_message = Message.objects.create(level=constants.INFO, text="Message {0}".format(i + 1),
                                                     author=self.bob, user_generated=True)
                new_message.sent_to_users.add(self.alice)
                messages.append(new_message)
                self.assertEqual(i + 1, self.alice_storage.new_count)

            self.assertEqual(5, self.alice_storage.new_count)

            self.alice_storage.update_last_checked()

            self.assertEqual(0, self.alice_storage.new_count)
            self.assertSequenceEqual([], list(self.alice_storage.new))

        def test_simple_filter(self):
            messages = self.alice_storage.all.filter(text="Read message")
            self.assertEqual(1, len(list(messages)))
            self.assertIn(self.read_message, list(messages))

        def test_and_filter(self):
            messages = self.alice_storage.all.filter(text="Read message", level=constants.INFO)
            self.assertEqual(1, len(list(messages)))
            self.assertIn(self.read_message, list(messages))

        def test_django_lookup_filter(self):
            messages = self.alice_storage.all.filter(text__startswith="Read")
            self.assertEqual(1, len(list(messages)))
            self.assertIn(self.read_message, list(messages))

        def test_q_filter(self):
            messages = self.alice_storage.all.filter(Q(text__startswith="Read") | Q(text__startswith="Bob"))
            self.assertEqual(2, len(list(messages)))
            self.assertIn(self.read_message, list(messages))
            self.assertIn(self.bob_message_to_group1, list(messages))

        def test_simple_exclude(self):
            messages = self.alice_storage.all.exclude(text="Read message")
            self.assertEqual(1, len(list(messages)))
            self.assertIn(self.bob_message_to_group1, list(messages))

        def test_and_exclude(self):
            messages = self.alice_storage.all.exclude(text="Read message", level=constants.INFO)
            self.assertEqual(1, len(list(messages)))
            self.assertIn(self.bob_message_to_group1, list(messages))

        def test_django_lookup_exclude(self):
            messages = self.alice_storage.all.exclude(text__startswith="Read")
            self.assertEqual(1, len(list(messages)))
            self.assertIn(self.bob_message_to_group1, list(messages))

        def test_q_exclude(self):
            messages = self.alice_storage.all.exclude(Q(text__startswith="Read") | Q(text__startswith="Bob"))
            self.assertEqual(0, len(list(messages)))

        def test_pagination(self):
            p = self.bob_storage.all.paginate(1)

            self.assertEqual(3, p.num_pages)

            page_1 = p.get_page(1)
            page_2 = p.get_page(2)
            page_3 = p.get_page(3)

            self.assertIn(self.read_message, list(page_1))
            self.assertIn(self.bob_message_to_group1, list(page_2))
            self.assertIn(self.alice_message_to_bob, list(page_3))
