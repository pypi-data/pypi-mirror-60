=====================
collective.sendinblue
=====================

.. image:: https://travis-ci.org/collective/collective.sendinblue.svg?branch=master
    :target: https://travis-ci.org/collective/collective.sendinblue


This package provides Sendinblue_ integration for Plone.
It allows you to link your Plone site to your Sendinblue account via a new configuration section.
Then, you can add a portlet to allow visitors to subscribe to one of your list (you can choose which one).
You can also add a portlet to simply redirect the user to your own Sendinblue subscription form (it will append user's email to your base url).

Version 2.x are tested with Plone 5.2.x.

Version 1.x are tested with Plone 4.3.x.
The versions build from the branch 1.x will stay compatible with Plone 4.3.x.
Please note that they do not provide the full functionality (no redirection portlet).


.. _Sendinblue: https://sendinblue.com


Features
--------

- multiple accounts / lists support : you can link more than one Sendinblue account to your site
- archive link : you can provide an URL that points to archives (that you manage manually)
- reCaptcha on subscription portlet (not on redirection portlet) to avoid spammers


Limitations
-----------

Integration of Sendinblue account is limited to 50 lists (which is huge).
This is linked to official API limitation (batched lists) but could be improved later.

It has been developed on Plone 4.3 & Plone 5.2. No other versions were tested.


Translations
------------

This product has been translated into

- English
- French


Installation
------------

Install collective.sendinblue by adding it to your buildout::

    [buildout]

    ...

    eggs =
        collective.sendinblue


and then running ``bin/buildout``


To do
-----

- Switch to SendinBlue API v3
- Add more tests
- If a Plone user is connected, use his email address to populate subscription portlet (default value)
- If a Plone user is connected, change the portlet form to a text if he's already subscribed


Contribute
----------

- Issue Tracker: https://github.com/collective/collective.sendinblue/issues
- Source Code: https://github.com/collective/collective.sendinblue


License
-------

The project is licensed under the GPLv2.
