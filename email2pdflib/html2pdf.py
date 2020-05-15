import os
import re
import shutil
from subprocess import Popen, PIPE
from fatal_exception import FatalException

WKHTMLTOPDF_EXTERNAL_COMMAND = 'wkhtmltopdf'
WKHTMLTOPDF_ERRORS_IGNORE = frozenset(
    [r'QFont::setPixelSize: Pixel size <= 0 \(0\)',
     r'Invalid SOS parameters for sequential JPEG',
     r'libpng warning: Out of place sRGB chunk',
     r'Exit with code 1 due to network error: ContentNotFoundError',
     r'Exit with code 1 due to network error: UnknownContentError'])


class HtmltoPdf(object):
    def __init__(self):
        if not shutil.which(WKHTMLTOPDF_EXTERNAL_COMMAND):
            raise FatalException(
                "eml2pdflib requires wkhtmltopdf to be installed"
                "Please look at the README.md for more info")

    def output_body_pdf(self, html, output_dir, pdfname):
        if not os.path.exists(output_dir):
            raise FatalException("output_path does not exist")

        output_path = self.__get_unique_version(
            os.path.join(output_dir, pdfname))

        wkh2p_process = Popen([WKHTMLTOPDF_EXTERNAL_COMMAND, '-q',
                               '--load-error-handling', 'ignore',
                               '--load-media-error-handling', 'ignore',
                               '--encoding', 'utf-8', '-', output_path],
                              stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, error = wkh2p_process.communicate(input=html)
        ret_code = wkh2p_process.returncode
        assert output == b''
        self.__process_errors(ret_code, error)

    def __get_unique_version(self, filename):
        # From here: http://stackoverflow.com/q/183480/27641
        counter = 1
        file_name_parts = os.path.splitext(filename)
        while os.path.isfile(filename):
            filename = "%s_%s%s" % (file_name_parts[0],
                                    '_' + str(counter),
                                    file_name_parts[1])
            counter += 1
        return filename

    def __process_errors(self, ret_code, error):
        stripped_error = str(error, 'utf-8')

        # suppress certain errors
        for error_pattern in WKHTMLTOPDF_ERRORS_IGNORE:
            (stripped_error, _) = re.subn(error_pattern, '', stripped_error)

        original_error = str(error, 'utf-8').rstrip()
        stripped_error = stripped_error.rstrip()

        if ret_code > 0 and original_error == '':
            raise FatalException("wkhtmltopdf failed with exit code " +
                                 str(ret_code) +
                                 ", no error output.")
        elif ret_code > 0 and stripped_error != '':
            raise FatalException("wkhtmltopdf failed with exit code " +
                                 str(ret_code) +
                                 ", stripped error: " + stripped_error)
        elif stripped_error != '':
            raise FatalException(
                "wkhtmltopdf exited with rc = 0 but produced \
                    unknown stripped error output " + stripped_error)
