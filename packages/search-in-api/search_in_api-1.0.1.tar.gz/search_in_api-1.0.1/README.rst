=============
Search in API
=============


.. image:: https://img.shields.io/pypi/v/search_in_api.svg
        :target: https://pypi.python.org/pypi/search_in_api

.. image:: https://img.shields.io/travis/archatas/search_in_api.svg
        :target: https://travis-ci.org/archatas/search_in_api

.. image:: https://pyup.io/repos/github/archatas/search_in_api/shield.svg
     :target: https://pyup.io/repos/github/archatas/search_in_api/
     :alt: Updates

.. image:: https://readthedocs.org/projects/search-in-api/badge/?version=latest
        :target: https://search-in-api.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




**Search in API** is a tool helping to debug import scripts or export APIs. It allows you to search for a specific tag
and value among multiple pages of an XML API endpoint or key and value among multiple pages of a JSON API endpoint.

* Free software: MIT license
* Documentation: https://search-in-api.readthedocs.io.


Use Case Example
----------------

Let's say, you have an XML API that provides a playlist of songs. It's a looooong paginated list and there is no search
implemented. You have an urge to find that particular song with a title having a word "Journey" and to check who
is playing it. If the songs are listed chronologically by the date added, you would need to search from page to page
until you finally get it. This tool does exactly that for you. There you can enter the URL of the first page of XML API or JSON API,
enter the tag or key "title", and the value "Journey", and a few moments later it will show you the page URLs of the API that
contain songs with the word "Journey" in it.

XML and JSON API Endpoints
--------------------------

The XML API endpoint should necessarily have ``/meta/next/`` node defining the URL of the next page as in `this XML example`_.

Similarly the JSON API endpoint should necessarily have the ``['meta']['next']`` key defining the URL of the next page as in `this JSON example`_.

.. _`this XML example`: https://raw.githubusercontent.com/archatas/search_in_api/master/tests/data/sample-data.xml

.. _`this JSON example`: https://raw.githubusercontent.com/archatas/search_in_api/master/tests/data/sample-data.json

Features
--------

* Search for pages with specific occurrences of tag/key and value in multi-page XML or JSON API endpoint.
* Command-line and graphical user interface.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
