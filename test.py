import imaplib
import email
import os
from lib.eml2html import EmailtoHtml
from lib.html2pdf import HtmltoPdf
from lib.html2img import HtmltoImage

EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
EMAIL_PSWD = os.environ['EMAIL_PSWD']
EMAIL_MAILBOX = os.environ['EMAIL_MAILBOX']
IMAP_SERVER = os.environ['IMAP_SERVER']


class EmailHelper(object):
    def __init__(self, IMAP_SERVER, EMAIL_ADDRESS,
                 EMAIL_PSWD, EMAIL_MAILBOX):
        # logs in to the desired account and navigates to the inbox
        self.mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        self.mail.login(EMAIL_ADDRESS, EMAIL_PSWD)
        self.mail.select()

    def get_emails(self):
        uids = self.mail.uid('SEARCH', 'ALL')[1][0].split()
        return uids

    def get_email_message(self, email_id):
        _, data = self.mail.uid('FETCH', email_id, '(RFC822)')
        raw_email = data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)
        return email_message


email_helper = EmailHelper(IMAP_SERVER, EMAIL_ADDRESS,
                           EMAIL_PSWD, EMAIL_MAILBOX)
email_to_html_convertor = EmailtoHtml()
html_to_pdf_convertor = HtmltoPdf()
html_to_img_convertor = HtmltoImage()
uids = email_helper.get_emails()

dir_path = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(dir_path, "outputs")

for uid in uids:
    email_message = email_helper.get_email_message(uid)
    html = email_to_html_convertor.convert(email_message)

    filename = uid.decode() + ".jpg"
    img_path = html_to_img_convertor.save_img(
        html.encode(), output_dir, filename)
    print(img_path)

    filename = uid.decode() + ".pdf"
    pdf_path = html_to_pdf_convertor.save_pdf(
        html.encode(), output_dir, filename)
    print(pdf_path)
