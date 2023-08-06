Introduction
============

*dramaTTS* is intended to provide a free solution for converting a drama / screen play text into a multi-voiced audio
recording using text-to-speech synthesis.

While *dramaTTS* provides a text parser to identify the speakers of each line/paragraph of the play and a bunch of
configuration options (e.g. for speaker voices) the actual text-to-speech synthesis and audio post-processing relies on
the external tools `Festival Speech Synthesis System`_ (short *festival*) and `Sound eXchange (SoX)`_ (short *sox*).

*dramaTTS* reads a text file, stores the voice configuration and schedules separate *festival* processes to render each
line/paragraph (i.e. a continuous text section read by on speaker) into wave-files, which are afterwards
post-processed/merged using *sox*.

The basic working principles of *dramaTTS* shall be illustrated on a short text example - a detailed explanation of
the different configuration options and features can be found in the :ref:`user_guide`.

Let's consider following example text (stored in a plain text file - e.g. example.txt):

.. code::


    1. Scene 1: A demonstration of "drama T T S"

    Bob and Mary Ann are having a conversation

    BOB

    Hi, Mary Ann how are you doing?

    MARY ANN

    Hi, Bob - I'm doing fine. How are you? (turns around as a loud noise is heard in the back) What was that?

When this text is imported, *dramaTTS* will analyze it for different continuous text section of the same content type
(which can for instance be a new scene title or content of a dialogue) and analyze the speaker of this section.
I.e. for the example above *dramaTTS* will identify following structure:

.. image::  parsed_example.png

The different colors indicate different content types - as can be seen the characters/speakers in the play and their
line count is identified and displayed in the table on the bottom right.

As a next step the voices for each character/speaker will be defined.

.. image::  speaker_params.png

Afterwards the text can be rendered to audio files.

.. image::  render_progress.png

The audio output can be played below.

.. raw:: html

    <audio controls="controls">
      <source src="../_static/example.wav" type="audio/wav">
      Your browser does not support the <code>audio</code> element.
    </audio>


Features
--------

As mentioned above *dramaTTS* consists of 2 main components: a script parser and a scheduler/configurator for
the audio-rendering.

The script parser features:

* configurable input file formatting (see :ref:`content_identifiers_tab`)
* syntax highlighting (identifies different content like new scenes, dialogue lines, narrative descriptions,...)
* text string substitutions supporting regular expressions
* some utility functions like sorting speakers according to their number of text lines

The audio-renderering part basically provides a front-end to *Festival* and *SoX* with following features supported:

* Altering of *Festival* voices (pitch, tempo and volume)
* support for multiple CPU cores to accelerate audio rendering (dispatches parallel processes for individual lines)
* using a *Festival* server for rendering is supported
* some post-processing: normalize all voices, combine audio files (lines -> scenes -> single project file)
* (re-)rendering of individual scenes or speakers


Licenses
--------

*dramaTTS*, Copyright (c) 2020 Thies Hecker

*dramaTTS* is free software released under the GPLv3 license (see the full disclaimer in COPYING_ and the LICENSE_
file for details).
It is written *python* and you can download the source code from `dramaTTS's gitlab page`_.

*dramaTTS* is realized using:

PyQt_, Copyright (c) Riverbank Computing Limited

and

setuptools_scm_, Copyright (c) Ronny Pfannschmidt.

While *dramaTTS* is a standalone application, it is of limited use without *Festival* and *SoX* being installed,
which provide the audio rendering (only script parsing including syntax highlighting, etc. is available).

While the *Festival* application itself and *SoX* are released under free software licenses as well,
specific components, which are commonly bundled with *Festival* (i.e. certain lexicons and voices) may be released
under non-free licenses.

For instance the *festlex-OALD* lexicon, which can be found among other files (incl. the source code of the latest
*Festival* release) on the `Festvox 2.5 release page`_ lexicon is restricted to non-commercial use only.

The :ref:`installing_festival` section will provide an example for a *Festival* distribution
based on *free* components only.

Please see the COPYING_ file in the source code repository for details on licenses and copyright disclaimers of the
individual components.


.. target-notes::

.. _`Festival Speech Synthesis System`: http://www.cstr.ed.ac.uk/projects/Festival/
.. _`Sound eXchange (SoX)`: http://sox.sourceforge.net/Main/HomePage
.. _LICENSE: https://gitlab.com/thecker/dramatts/blob/master/LICENSE
.. _PyQt: https://wiki.python.org/moin/PyQt
.. _setuptools_scm: https://github.com/pypa/setuptools_scm/
.. _COPYING: https://gitlab.com/thecker/dramatts/blob/master/COPYING
.. _`dramaTTS's gitlab page`: https://gitlab.com/thecker/dramatts
.. _`Festival license`: https://github.com/festvox/festival/blob/master/COPYING
.. _`Sox license`: https://sourceforge.net/p/sox/code/ci/master/tree/COPYING
.. _`Festvox 2.5 release page`: http://festvox.org/packed/festival/2.5/
.. _`Festvox github page`: https://github.com/festvox/
.. _Anaconda: https://www.anaconda.com/distribution/#download-section
.. _miniconda: https://docs.conda.io/en/latest/miniconda.html
.. _`Festival 2.5 version including precompiled binaries for Windows`: https://sourceforge.net/projects/e-guidedog/files/related%20third%20party%20software/0.3/festival-2.5-win.7z/download
.. _/utils folder: https://gitlab.com/thecker/dramatts/tree/master/utils
.. _`SoX sourceforge page`: https://sourceforge.net/projects/sox/files/sox/14.4.2/
.. _`CMU_ARCTIC speech synthesis databases`: http://festvox.org/cmu_arctic/index.html
.. _here: http://festvox.org/packed/festival/2.5/voices/
