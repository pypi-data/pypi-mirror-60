# Copyright 2020 Louis Paternault
#
# This file is part of Paste2SMS.
#
# Paste2SMS is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Paste2SMS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with Paste2SMS.  If not, see <http://www.gnu.org/licenses/>.

"""Send SMS using API of French provider "Free Mobile".

French provider `Free Mobile <http://mobile.free.fr>`__ provides a free API to send SMS to oneself.

Configuration file
------------------

.. code-block:: ini

  [general]
  provider = freemobile
  editor = gedit --wait --standalone {}

  [provider:freemobile]
  user = 12345678
  password = s3cr37

This provider has to mandatory configuration options: ``user`` and ``password``, which are:

- ``user``: your user login on `http://mobile.free.fr <http://mobile.free.fr>`__;
- ``password``: the key given on `http://mobile.free.fr <http://mobile.free.fr>`__, in *Gérer mon compte* > *Mes options* > *Notification par SMS*.

"""

import logging

import requests

from .. import P2SException

ERRORS = {
    400: "Un des paramètres obligatoires est manquant.",
    402: "Trop de SMS ont été envoyés en trop peu de temps.",
    403: "Le service n'est pas activé sur l'espace abonné, ou login / clé incorrect.",
    500: "Erreur côté serveur. Veuillez réessayer ultérieurement.",
}


def send_sms(content, *, config):
    """Send an SMS.

    Arguments:

    - content: Message to be sent (as a string).
    - config: Configuration (as a configparser.ConfigParser() object).

    Raise a P2SException if SMS could not be sent.
    """
    response = requests.get(
        "https://smsapi.free-mobile.fr/sendmsg",
        params={"user": config["user"], "pass": config["password"], "msg": content,},
    )
    if response.status_code == 200:
        return
    raise P2SException(
        "{} ({}).".format(
            ERRORS.get(response.status_code, response.reason), response.status_code,
        ),
        level=logging.ERROR,
    )
