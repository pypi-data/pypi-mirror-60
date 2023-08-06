.. -*- coding: utf-8 -*-

Changes
-------

4.0a6 (2020-01-29)
~~~~~~~~~~~~~~~~~~

* Nicer rendering of the main Lit page

* Simpler way to open the Lit page of a tourney from its management window

* Allow to save partial results, to be on the safe side when there are lots of boards

* Show the "hosting club" on all printouts, if present


4.0a5 (2020-01-25)
~~~~~~~~~~~~~~~~~~

* Remove "email", "language" and "phone" from players data

* Remove player's rate from participants printout

* Omit the player's club in the ranking printout for international tourneys

* Add the player's nationality in matches and results printouts

* Add an "hosting club" to tournaments


4.0a4 (2020-01-18)
~~~~~~~~~~~~~~~~~~

* New association between clubs and users: now a user may add a
  championship/tourney/rating/player only to clubs he either owns or is associated with

* Add a link to send an email to the instance' admin on the login panel


4.0a3 (2020-01-13)
~~~~~~~~~~~~~~~~~~

* Use a three-state flag for the player's *agreed privacy*: when not explicitly expressed, SoL
  assumes they are publicly discernible if they participated to tournaments after January 1,
  2020

* Player's first and last names must be longer that one single character


4.0a2 (2020-01-11)
~~~~~~~~~~~~~~~~~~

* Fix issue with UI language negotiation

* Use the better maintained `Fomantic-UI`__ fork of `Semantic-UI`__ in the “Lit” interface

__ https://fomantic-ui.com/
__ https://semantic-ui.com/

* New tournaments *delay compatriots pairing* option

* Technicalities:

  * Official repository is now https://gitlab.com/metapensiero/SoL

  * NixOS__ recipes (thanks to azazel@metapensiero.it)

__ https://nixos.org/


4.0a1 (2018-08-06)
~~~~~~~~~~~~~~~~~~

.. warning:: Backward **incompatible** version

   This release uses a different algorithm to crypt the user's password: for this reason
   previous account credentials cannot be restored and shall require manual intervention.

   It's **not** possible to *upgrade* an existing SoL3 database to the latest version.

   However, SoL4 is able to import a backup of a SoL3 database made by ``soladmin backup``.

* Different layout for matches and results printouts, using two columns for the competitors to
  improve readability (suggested by Daniele)

* New tournaments *retirements policy*

* New "women" and "under xx" tourney's ranking printouts

* New “self sign up” procedure

* New “forgot password” procedure

* New "agreed privacy" on players

* Somewhat prettier “Lit” interface, using `Semantic-UI tables`__

* Technicalities:

  * Development moved to GitLab__

  * Officially supported on Python 3.6 and 3.7, not anymore on <=3.5

  * Shiny new pytest-based tests suite

  * Uses `python-rapidjson`__ instead `nssjson`__, as I officially declared the latter as
    *abandoned*

  * Uses `PyNaCl`__ instead of `cryptacular`__, as the former is much better maintained

  * "Users" are now a separated entity from "players": now the login "username" is a mandatory
    email and the password must be longer than **five** characters (was three before)


__ https://semantic-ui.com/collections/table.html
__ https://gitlab.com/metapensiero/SoL
__ https://pypi.org/project/python-rapidjson/
__ https://pypi.org/project/nssjson/
__ https://pypi.org/project/PyNaCl/
__ https://pypi.org/project/cryptacular/
