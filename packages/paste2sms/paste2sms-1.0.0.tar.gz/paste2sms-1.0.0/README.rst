paste2sms 📲 Send clipboard content as a SMS
============================================

`paste2sms` is a small tool which send the content of your clipboard as a SMS: do you want to share that cool link you just found (on your computer) to your friend? Copy it, and run `paste2sms` to send it as a SMS.

.. image:: https://framagit.org/spalax/paste2sms/raw/master/doc/_static/screencast.gif

What's new?
-----------

See `changelog
<https://git.framasoft.org/spalax/paste2sms/blob/master/CHANGELOG.md>`_.

Download and install
--------------------

* From sources:

  * Download: https://pypi.python.org/pypi/paste2sms
  * Install::

        python3 setup.py install

* From pip::

    pip install paste2sms

* Quick and dirty Debian (and Ubuntu?) package

  This requires `stdeb <https://github.com/astraw/stdeb>`_ (and `setuptools-scm <https://pypi.org/project/setuptools-scm/>`_) to be installed::

      python3 setup.py --command-packages=stdeb.command bdist_deb
      sudo dpkg -i deb_dist/paste2sms-<VERSION>_all.deb

  This will also install the launcher.


Documentation
-------------

* The compiled documentation is available on `readthedocs
  <http://paste2sms.readthedocs.io>`_

* To compile it from source, download and run::

      cd doc && make html
