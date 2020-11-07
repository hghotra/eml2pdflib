FROM python:3.6

COPY . /root/email2pdf

RUN cd /root \
        && apt-get update \
        && apt-get install -y xfonts-75dpi xfonts-base getmail4 \
        && wget -O wkhtmltox.deb 'https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb' \
        && dpkg -i *.deb \
        && pip install -r email2pdf/requirements.txt 

USER user
