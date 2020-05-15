# email2pdflib

An `eml` to `pdf` conversion helper library built by refactoring the `email2pdf` script by *Andrew Ferrier* that can be found here: https://github.com/andrewferrier/email2pdf

### Running (Docker Container)
```
make builddocker
make rundocker_interactive
```

## Installing Dependencies

Before you can use email2pdf, you need to install some dependencies. The
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
