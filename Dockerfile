FROM python:3.6

COPY . /root/email2pdf

RUN cd /root \
        && apt-get update \
        && apt-get install -y xfonts-75dpi xfonts-base getmail4 \
        && wget -O wkhtmltox.deb 'https://downloads.wkhtmltopdf.org/0.12/0.12.5/wkhtmltox_0.12.5-1.stretch_amd64.deb' \
        && dpkg -i *.deb \
        && pip install -r email2pdf/requirements.txt \
        && cp email2pdf/email2pdf /usr/local/bin

USER www-data 
