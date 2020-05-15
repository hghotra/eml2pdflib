# email2pdflib

An `eml` to `pdf` conversion helper library built by refactoring the `email2pdf` script by *Andrew Ferrier* that can be found here: https://github.com/andrewferrier/email2pdf

## Installing Dependencies

Before you can use `email2pdflib`, you need to install some dependencies. The
instructions here are split out by platform:

### Debian/Ubuntu

* [wkhtmltopdf](http://wkhtmltopdf.org/) - Install the `.deb` from
  http://wkhtmltopdf.org/ rather than using apt-get to minimise the
  dependencies you need to install (in particular, to avoid needing a package
  manager).

* [getmail](http://pyropus.ca/software/getmail/) - getmail is optional, but it
  works well as a companion to email2pdf. Install using `apt-get install
  getmail`.

* Others - there are some other Python library dependencies. Run `make
  builddeb` to create a `.deb` package, then install it with `dpkg -i
  mydeb.deb`. This will prompt you regarding any missing dependencies.

### OS X

* [wkhtmltopdf](http://wkhtmltopdf.org/) - Install the package from
  http://wkhtmltopdf.org/downloads.html.

* [getmail](http://pyropus.ca/software/getmail/) - TODO: This hasn't been
  tested, so there are no instructions here yet! Note that getmail is
  optional.

* Install [Homebrew](http://brew.sh/)

* `xcode-select --install` (for lxml, because of
  [this](http://stackoverflow.com/questions/19548011/cannot-install-lxml-on-mac-os-x-10-9))

* `brew install python3` (or otherwise make sure you have Python 3 and `pip3`
  available).

* `brew install libmagic`

* `pip3 install -r requirements.txt`

## Usage

Please look at the `test.py` for an example of how to use the library.

```
import imaplib
import email
import os
from lib.eml2html import EmailtoHtml
from lib.html2pdf import HtmltoPdf

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
uids = email_helper.get_emails()

dir_path = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(dir_path, "pdfs")

for uid in uids:
    email_message = email_helper.get_email_message(uid)
    html = email_to_html_convertor.convert(email_message)
    filename = uid.decode() + ".pdf"
    pdf_path = html_to_pdf_convertor.save_pdf(
        html.encode(), output_dir, filename)
    print(pdf_path)

```
