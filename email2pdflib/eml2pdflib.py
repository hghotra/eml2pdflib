#!/usr/bin/env python3

import functools
import html
import mimetypes
import re
import sys
import magic
from bs4 import BeautifulSoup
from utils import can_url_fetch
from email.header import decode_header
from fatal_exception import FatalException

assert sys.version_info >= (3, 4)

mimetypes.init()
FORMATTED_HEADERS_TO_INCLUDE = frozenset(['Subject', 'From', 'To', 'Date'])
IMAGE_LOAD_BLACKLIST = frozenset(['emltrk.com', 'trk.email', 'shim.gif'])


class EmailtoHtml(object):
    def __init__(self):
        pass

    def convert(self, eml, headers=True):
        self.eml = eml
        payload = self.__handle_message_body()
        payload = self.__remove_invalid_urls(payload)

        if headers:
            header_info = self.__get_formatted_header_info()
            payload = header_info + payload

        return payload

    def __handle_message_body(self):
        part = self.__part_by_content_type(self.eml, "text/html")
        if part is not None:
            return self.__handle_html_message_body(part)

        part = self.__part_by_content_type(self.eml, "text/plain")
        if part is not None:
            payload = self.__handle_plain_message_body(part)
            return (payload, set())

        raise FatalException("Email message has no body")

    def __handle_html_message_body(self, part):
        payload = part.get_payload(decode=True)
        charset = part.get_content_charset()
        if not charset:
            charset = 'utf-8'

        payload = re.sub(r'cid:([\w_@.-]+)',
                         functools.partial(self.__cid_replace),
                         str(payload, charset))

        return payload

    def __handle_plain_message_body(self, part):
        if part['Content-Transfer-Encoding'] == '8bit':
            payload = part.get_payload(decode=False)
            assert isinstance(payload, str)
        else:
            payload = part.get_payload(decode=True)
            assert isinstance(payload, bytes)
            charset = part.get_content_charset()
            if not charset:
                charset = 'utf-8'

            payload = str(payload, charset)
            payload = html.escape(payload)
            payload = "<html><body><pre>\n" + \
                payload + "\n</pre></body></html>"

        return payload

    def __get_formatted_header_info(self):
        header_info = ""

        for header in FORMATTED_HEADERS_TO_INCLUDE:
            if self.eml[header]:
                decoded_string = self.__get_utf8_header(self.eml[header])
                header_info = header_info + '<b>' + header + '</b>: '\
                    + decoded_string + '<br/>'

        return header_info + '<br/>'

    def __get_utf8_header(self, header):
        # There is a simpler way of doing this here:
        # http://stackoverflow.com/a/21715870/27641. However, it doesn't
        # seem to work, as it inserts a space between certain elements
        # in the string that's not warranted/correct.
        decoded_header = decode_header(header)
        hdr = ""
        for element in decoded_header:
            if isinstance(element[0], bytes):
                hdr += str(element[0], element[1] or 'ASCII')
            else:
                hdr += element[0]
        return hdr

    def __cid_replace(self, matchobj):
        cid = matchobj.group(1)
        image_part = self.__find_part_by_content_id(self.eml, cid)

        if image_part is None:
            image_part = self.__find_part_by_content_type_name(self.eml, cid)

        if image_part is not None:
            assert image_part['Content-Transfer-Encoding'] == 'base64'
            image_base64 = image_part.get_payload(decode=False)
            image_base64 = re.sub("[\r\n\t]", "", image_base64)
            image_decoded = image_part.get_payload(decode=True)
            mime_type = self.__get_mime_type(image_decoded)
            return "data:" + mime_type + ";base64," + image_base64
        else:
            raise FatalException(
                "Could not find image cid " + cid + " in email content.")

    def __get_mime_type(self, buffer_data):
        # pylint: disable=no-member
        if 'from_buffer' in dir(magic):
            mime_type = magic.from_buffer(buffer_data, mime=True)
            if type(mime_type) is not str:
                # Older versions of python-magic seem to output bytes for the
                # mime_type name. As of Python 3.6+, it seems to be outputting
                # strings directly.
                mime_type = str(
                    magic.from_buffer(buffer_data, mime=True), 'utf-8')
        else:
            m_handle = magic.open(magic.MAGIC_MIME_TYPE)
            m_handle.load()
            mime_type = m_handle.buffer(buffer_data)

        return mime_type

    def __find_part_by_content_type_name(self, message, content_type_name):
        for part in message.walk():
            part_content_type = part.get_param('name', header="Content-Type")
            if part_content_type == content_type_name:
                return part
        return None

    def __find_part_by_content_id(self, message, content_id):
        for part in message.walk():
            if part['Content-ID'] in (content_id, '<' + content_id + '>'):
                return part
        return None

    def __part_by_content_type(self, message, content_type):
        for part in message.walk():
            if part.get_content_type() == content_type:
                return part
        return None

    def __remove_invalid_urls(self, payload):
        soup = BeautifulSoup(payload, "html5lib")

        for img in soup.find_all('img'):
            if img.has_attr('src'):
                src = img['src']
                lower_src = src.lower()
                if lower_src == 'broken':
                    del img['src']
                elif not lower_src.startswith('data'):
                    found_blacklist = False

                    for image_load_blacklist_item in IMAGE_LOAD_BLACKLIST:
                        if image_load_blacklist_item in lower_src:
                            found_blacklist = True

                    if not found_blacklist:
                        if not can_url_fetch(src):
                            del img['src']
                    else:
                        del img['src']

        return str(soup)
