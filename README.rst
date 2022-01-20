.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

==================
edi.substanceforms
==================

The Add-On edi.substanceforms has been developed for the free Open Source Web Content Management System Plone.

Features
--------

- employees in the printing and paper processing industry can search for chemical products used in the manufacturing process with the least impact on human health
- they can manage, create, update and delete those substances and substance mixtures


Documentation
-------------

The full documentation of this project can be found online here: https://substanceforms.educorvi.de


Translations
------------

This product and the full documentation is written in German.

Installation
------------

Please make sure, that pg_config is installed.
This is part of postgresql-devel, and it can be installed with the following command on an Ubuntu/Debian system::

    sudo apt install libpq-dev

Install edi.substanceforms by adding it to your buildout::

    [buildout]

    ...

    eggs =
        edi.substanceforms


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/educorvi/edi.substanceforms/issues
- Source Code: https://github.com/educorvi/edi.substanceforms
- Documentation: https://substanceforms.educorvi.de


Support
-------

If you are having issues, please let me know.
Feel free to contact me here: seppo.walther@educorvi.de


License
-------

The project is licensed under the MIT License.
