=====================================
Welcome to paste2sms's documentation!
=====================================

`paste2sms` is a small tool which send the content of your clipboard as a SMS: do you want to share that cool link you just found (on your computer) to your friend? Copy it, and run `paste2sms` to send it as a SMS.

A list of frequently asked questions is available :ref:`there <faq>`.

.. only:: html

  .. image:: _static/screencast.gif

.. toctree::
   :maxdepth: 1
   :hidden:
   :glob:

   faq
   provider/*

.. contents::
   :local:
   :depth: 1

Rationale
=========

I mainly use my computer to browse; my wife mainly uses her cell phone to browse. When I wanted to share an URL with her, I could:

- send her an email (too cumbersome for this task);
- copy the URL in a file, transfer it to my phone by Bluetooth, open it from my phone, copy the link and paste it in a SMS (even more cumbersome).

With `paste2sms`, I simply copy the link, run `paste2sms` (which send the content of the clipboard as an SMS to my phone), and transfer this SMS.

Configuration file
==================

A ``paste2sms.conf`` file must exists on your computer. It may be located in any directory of ``XDG_CONFIG_DIRS`` (typically ``~/.config/paste2sms.conf``. An example is:

.. code-block:: ini

  [general]
  provider = freemobile
  editor = gedit --wait --standalone {}

  [provider:freemobile]
  user = 12345678
  password = s3cr37

- Section ``general``:

  - ``editor``: Command line to be executed to edit the content of the SMS before sending it (where ``{}`` is replaced by a temporary file name). Can be ommited: in this case, the SMS is sent directly.
  - ``provider``: Provider used to send the SMS. See :ref:`providers`.

- Section ``provider:FOO``:

  This section contains the options of cell phone provider `FOO`. Each provider has its own set of options. See :ref:`providers`.

.. _providers:

Cell phone providers
====================

Here is the list of supported cell phone providers.

Right now, the only supported one is the one I use. `Pull requests <https://framagit.org/spalax/paste2sms/merge_requests>`__ are welcome!

.. currentmodule:: paste2sms

.. autosummary::
   :toctree: provider

   provider.freemobile


Command line arguments
======================

Here are the command line options for `paste2sms`.

.. argparse::
    :module: paste2sms.__main__
    :func: commandline_parser
    :prog: paste2sms

Download and install
====================

See the `main project page <http://git.framasoft.org/spalax/paste2sms>`_ for
instructions, and `changelog
<https://git.framasoft.org/spalax/paste2sms/blob/master/CHANGELOG.md>`_.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
