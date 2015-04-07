OneResumé - 
=========================================

|image_pypi| |image_downloads| |image_license| |passing| |quality| |Coverage Status|

* Free and open-source software: ASL2 license
* Blog: http://virantha.com/category/projects/one_resume
* Documentation: http://virantha.github.io/one_resume/html
* Source: https://github.com/virantha/one_resume

Features
########

* Keep your resumé content in simple text files and automatically generate different versions
  of your resumés in multiple formats (currently supports generating text and Microsoft Word .docx format resumés)
* Allows you to break up your resumé content into multiple files, so you can pick and choose the sections you want for each generated version
    * For example, if you want one resumé with your publications, but want to skip them for a shorter version, you can maintain the publications
      list in a separate input file, and keep both generated resumés synchronized with the other content.
* Plugin architecture, so you can easily extend to other formats (LaTex coming soon)

Usage:
######

OneResumé can be run in single resumé mode, or batch mode (in order to generate multiple different resumés in one go).  The former usage is shown
below:

::

    one_resume.py single -t template_filename -y resumé_content_filename -o output_filename -f Text

The ``-f`` option is the format you want to use, currently either ``Text`` or ``Word``.  The templates and content files
will be discussed in the next section.

If you want to run in batch mode:

::

    one_resume.py batch -c config.yml

The ``config.yml`` configuration file is a YAML_ file structured as follows:

::

    - data: sources/resumé1.yaml
      outputs: 
        -   
            format: Word
            template: sources/resumé-template1.docx
            output: generated/Resumé_standard.docx

    - data: sources/resumé1.yaml
      outputs: 
        -   
            format: Text
            template: sources/resumé-template1.txt
            output: generated/Resumé_standard.txt

    - data: sources/resumé1.yml
      outputs: 
        -   
            format: Word
            template: sources/resumé-template-short.docx
            output: generated/Resumé_short.docx

    - data: sources/resumé-jobseeker.yml
      outputs: 
        -   
            format: Word
            template: sources/resumé-template-jobseeker.docx
            output: generated/Resumé_jobseeker.docx


In this example, we are generating 4 different resumés, 3 of which are Word format, and 1 of which is text.  Three of them
use the same resumé content, with one of them presumably using that content to generate a shortened version (with a different template file). 
The fourth one uses a customized resumé content, perhaps with different wording, to generate a specialized resumé.  

Now, let's take a look at how the resumé content and output text files are structured.

Writing Resumé Content
----------------------
Resumé content is written using the YAML_ format.  The content is broken up into sections, with each section consisting of a list (can be just a single item list)
of content.  The example below is pretty self-explanatory:

.. code-block:: yaml

    blah:



Installation
############
Please note that the lxml python library requires a C compiler.  On Mac OS X, you need to make
sure you have XCode plus the the XCode command line utilities installed:

::

    $ xcode-select --install

Then, it's simply a matter of:

::

    $ pip install one_resume

Disclaimer
##########

The software is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

.. _YAML: http://en.wikipedia.org/wiki/YAML
.. |image_pypi| image:: https://badge.fury.io/py/one_resume.png
   :target: https://pypi.python.org/pypi/one_resume
.. |image_downloads| image:: https://pypip.in/d/one_resume/badge.png
   :target: https://crate.io/packages/one_resume?version=latest
.. |image_license| image:: https://pypip.in/license/one_resume/badge.png
.. |passing| image:: https://scrutinizer-ci.com/g/virantha/one_resume/badges/build.png?b=master
.. |quality| image:: https://scrutinizer-ci.com/g/virantha/one_resume/badges/quality-score.png?b=master
.. |Coverage Status| image:: https://coveralls.io/repos/virantha/one_resume/badge.png?branch=develop
   :target: https://coveralls.io/r/virantha/one_resume
