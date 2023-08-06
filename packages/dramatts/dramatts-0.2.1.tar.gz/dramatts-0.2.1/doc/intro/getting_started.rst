Getting started
===============

Installing *dramaTTS*
---------------------

You will need a python3 distribution installed and for most convenience you should have either the *pip* or *conda*
package manager installed.

On linux you will most likely have python and pip already installed - if not you should be able to install them with
distributions package-manager.

E.g. for *debian* based system like *ubuntu* just run:

.. code::

    sudo apt-get python3-pip

or on *arch* based systems:

.. code::

    sudo pacman -S python-pip

For Windows users I would recommend to install Anaconda_ or miniconda_, which will provide the *conda* package
manager (make sure to get the python3 - not the python2 - version!).

To install *dramaTTS* with pip:

.. code::

    pip install dramatts

Note, that on some distributions you may install python2 and python3 in parallel. In such cases you should make sure,
that you not using a pip for your python2 environment to install *dramaTTS*. Eventually you need to use pip3 as a command.
You can check if you are using the correct pip by calling:

.. code::

    pip --version

To install *dramaTTS* with conda:

.. code::

    conda install -c thecker dramatts

In both cases pip or conda should download all required dependencies and should be able to launch the program.
To do that just type:

.. code::

    python -m dramatts.dramatts_gui

The GUI should pop up and you can import text files, define roles etc., but you will not be able render audio unless
you have installed *Festival* (and its components) and *SoX*.

.. _installing_festival:

Installing Festival without non-free components
-----------------------------------------------

While many linux distributions include pre-built packages for *Festival* they often include non-free components like
*festlex-OALD*. Therefore the safest way to create a *free* *Festival* distribution is to compile from source.
To form a *free* distribution following components could be used:

* Festival 2.5 (main application)
* Edinburgh Speech Tools (EST) - required to compile *Festival*
* festlex_CMU (lexicon)
* festlex_POSLEX (lexicon)
* festvox_cmu_us_slt_cg (female voice)
* festvox_cmu_us_rms_cg (male voice)

All components can be downloaded at CMU's (Carnegie Mellon University) `Festvox 2.5 release page`_. The source
code of *Festival* and *EST* can also be cloned from the `Festvox github page`_.

To compile the code follow the instructions in the INSTALL file included in *Festival*.

Note, that more voices can be found at the *Festvox* page (although some might require e.g. additional lexicons and
thus won't be working with the selected components above). Additionally voices may also be altered in tempo and pitch in
*dramaTTS* (by post-processing with *SoX*) to create more than one speaker per voice.

Building *Festival* from source is based on the autotools-toolchain - so it shouldn't be a problem on GNU/linux, but
may be complicated on MS Windows.

Fortunately the eGuideDog team has created compile-instructions for Windows and even provides a
`Festival 2.5 version including precompiled binaries for Windows`_ (which does not include the problematic
*festlex-OALD* lexicon).

In order to use *Festival* under Windows with *dramaTTS* you will need to copy the *text2wave.bat* (see
the `/utils folder`_) to your *Festival* installation.

Make sure to adjust the paths in *text2wave.bat*, if you did not install *Festival* in C:\\Festival.

Installing SoX
--------------

Under linux you will most likely have a pre-build package for *SoX*.
Building from source is probably not required.

Binaries for Windows can be found on the `SoX sourceforge page`_.

Configuring locations of external tools in *dramaTTS*
-----------------------------------------------------

dramaTTS will try to determine the install locations of *Festival* and *SoX* automatically.
This should most likely work under linux, if you installed the tools from the official packages (or put the location of
the binaries in your PATH).

You can see, if the tools where found in the log windows of *dramaTTS*. A check will be performed each time *dramaTTS*
is started - if all tools are configured correctly you will see messages like this in the log.

.. image::  check_for_tools.png

Under windows you will most likely have to define the tool locations manually.

To do that, just go to the :ref:`preferences_tab` in the *dramaTTS* GUI and specify the file locations.

If you used the *Festival* version provided by the link above the pre-compiled binaries are located in:

..Festival\\src\\main

After you specified a new tool location, you should save the preferences and restart *dramaTTS* to make the changes
become effective.

.. _`Festival Speech Synthesis System`: http://www.cstr.ed.ac.uk/projects/Festival/
.. _`Sound eXchange (SoX)`: http://sox.sourceforge.net/Main/HomePage
.. _LICENSE: https://gitlab.com/thecker/dramatts/blob/master/LICENSE
.. _PyQt: https://wiki.python.org/moin/PyQt
.. _setuptools_scm: https://github.com/pypa/setuptools_scm/
.. _COPYING: https://gitlab.com/thecker/dramatts/blob/master/COPYING
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