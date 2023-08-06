"""Main test code."""
from django.core import mail
from django.test import TestCase

from dmdm.mail import send_mail


class TestDMDM(TestCase):
    """Main test class."""
    def test_send_mail(self):
        """Test to send a mail."""
        subject = 'subject'
        from_email = 'sender@example.org'
        recipient_list = ['someone@example.com']

        self.assertEqual(len(mail.outbox), 0)

        message = '## This is a mail\n\nwith *some* markup'
        send_mail(subject, message, from_email, recipient_list)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('<h2>', mail.outbox[0].alternatives[0][0])
        self.assertNotIn('<h1>', mail.outbox[0].alternatives[0][0])

        send_mail(subject, 'test_email_template.md', from_email, recipient_list, {'template_variable': 'value'})

        self.assertEqual(len(mail.outbox), 2)
        self.assertIn('<h1>', mail.outbox[1].alternatives[0][0])
        self.assertNotIn('<h2>', mail.outbox[1].alternatives[0][0])
        self.assertIn('value', mail.outbox[1].alternatives[0][0])
