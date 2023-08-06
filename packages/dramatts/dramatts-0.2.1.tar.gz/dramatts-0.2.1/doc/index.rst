.. dramaTTS documentation master file, created by
   sphinx-quickstart on Wed Jan 29 09:06:59 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to dramaTTS's documentation!
====================================

About
-----

*dramaTTS* parses scripts (plain text files) for theatre/screen plays and converts them into a multi-voice audio plays
(wave-files).

While the script parsing functionality is provided by the *dramaTTS* program itself, it relies on external tools for
the audio processing:

* The `Festival Speech Synthesis System`_ (herein referred to as *Festival*) is used for speech synthesis
* `Sound eXchange (SoX)`_  for audio post-processing.

*SoX*, *Festival* as well as voices and lexicons for *Festival* have to be installed in order to create audio output
with *dramaTTS* (see :doc:`intro/getting_started`).

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   intro/introduction
   intro/getting_started
   user_guide/user_guide
   api_ref/api_ref

Links
=====

.. target-notes::

.. _`Festival Speech Synthesis System`: http://www.cstr.ed.ac.uk/projects/Festival/
.. _`Sound eXchange (SoX)`: http://sox.sourceforge.net/Main/HomePage


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
