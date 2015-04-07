OneResumé - Usage Guide
=========================================
OneResumé is a data-driven resumé generator for text and Microsoft Word
documents.  Write your resumé content in YAML_ and quickly and easily generate
multiple versions and formats of your resumé using this program.

|image_pypi| |image_downloads| |image_license| |passing| |quality| |Coverage Status|

* Free and open-source software: ASL2 license
* Blog: http://virantha.com/category/projects/one_resume
* Documentation: http://virantha.github.io/one_resume/html
* Source: https://github.com/virantha/one_resume

Features
########

- Keep your resumé content in simple text files and automatically generate
  different versions of your resumés in multiple formats (currently supports
  generating text and Microsoft Word .docx format resumés)

- Allows you to break up your resumé content into multiple files, so you can
  pick and choose the sections you want for each generated version. For
  example, if you want one resumé with your publications, but want to skip them
  for a shorter version, you can maintain the publications list in a separate
  input file, and keep both generated resumés synchronized with the other
  content.

- Plugin architecture, so you can easily extend to other formats (LaTex coming soon)

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

.. code-block:: yaml

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

    contact:
        -
            name: S. Holmes
            address: 221B Baker Street, St Marylebone, London, England
            phone: None
            email: sherlock@holmesconsulting.com
            www: http://www.gotcrime.com

    skills:
        - 
            type: Current
            skill_list:  > 
                Crime solving, cigarette-ash classification, crypto-analysis, disguise

        -
            type: Past
            skill_list: > 
                Fencing, violin

    education:
        - 
            degree: BA
            university: Christ Church College
            address: Oxford, England
            field: Chemistry
            date: 1876
            gpa: 5.0
        - 
            degree: MA 
            university: Sidney Sussex
            address: Cambridge
            date: 1878
            field: Criminology
            gpa: 3.9

    experience:
        - 
            company: Baker Street Detectives
            location: London
            position: Consulting Detective
            date: "1880 to 1903"
            summary: >
                Brought several notorious criminals to justice.  Supported the intelligence services and recovered key
                government property. 

        - 
            company: Beekeeping Solutions 
            location: Sussex Downs
            position: Beekeeper
            date: "1904-1914"
            summary: >
                Made honey.


You can also split the content up into several different files.  For example, the top level file could just be written as:

.. code-block:: yaml

    contact:
        -
            name: S. Holmes
            address: 221B Baker Street, St Marylebone, London, England
            phone: None
            email: sherlock@holmesconsulting.com
            www: http://www.gotcrime.com

    skills: !include data_skills.yml

    education: !include data_education.yml

    experience: !include data_experience.yml
 


Writing Templates for Text Resumés
----------------------------------
The text resumé generator uses the Mako_ templating engine.  Here's an example template that can be used to output
the above data content into a text file:

.. code-block:: python

    % for contact in d["contact"]:
    ${contact['name']}
    ${contact['phone']}
    ${contact['email']}
    ${contact['www']}
    % endfor
    =========================================

    SKILLS:
    -------
    % for skill in d["skills"]:
      ${skill['type']}: 
        ${s._wrap(2,skill['skill_list'])}
    % endfor

    EDUCATION:
    ----------
    % for e in d['education']:
      ${e['degree']} from ${e['university']} in ${e['field']} (${e['date']})
    % endfor

    EXPERIENCE:
    ----------
    % for e in d['experience']:
      ${e['position']} (${e['date']})
      ${e['company']}, ${e['location']}
      -----------------------------------
        ${s._wrap(2,e['summary'])}

    % endfor

The main things to note are:

- The resume content from the YAML file is stored as a dictionary in ``d``.  
- Each top-level entry in this dictionary is a list that can be iterated over using Mako syntax.
- There is a helper function called ``s._wrap`` that can be used to indent some text with the 
  given number of spaces.

Using this template, and the data content above, would yield the following text:

::

    S. Holmes
    12-3456
    sherlock@holmesconsulting.com
    http://www.gotcrime.com
    =========================================

    SKILLS:
    -------
      Current: 
        Crime solving, cigarette-ash classification, crypto-analysis, disguise
      Past: 
        Fencing, violin

    EDUCATION:
    ----------
      BA from Christ Church College in Chemistry (1876)
      MA from Sidney Sussex in Criminology (1878)

    EXPERIENCE:
    ----------
      Consulting Detective (1880 to 1903)
      Baker Street Detectives, London
      -----------------------------------
        Brought several notorious criminals to justice.  Supported the
        intelligence services and recovered key government property.

      Beekeeper (1904-1914)
      Beekeeping Solutions, Sussex Downs
      -----------------------------------
        Made honey.


Writing Templates for Word Resumés
----------------------------------
Word templates are just regular ``.docx`` files. Please note that you cannot use the old
Word 97 ``.doc`` format.    You can format it however you want, including bullets and styles.  However, tables
are *not* supported at this time.  Here's some simple content you might type into a word document to generate
a resume from the above YAML:

::

    [!Contact]

    <[name]
    [email]
    [www]
    [phone]
    >

    [Experience]
    <[company] – [location] [date]
    [position]
    [summary]
    >
    [Education]
    <[degree] ([university]) in [field] [date]
    >
    [Skills|Mad Skillls]
    <[type] – [skill_list]>


The syntax is as follows:

- Section and item names are enclosed in brackets (``[`` and ``]``)
- Looping over sections is done using the ``<`` character for starting the loop, and ``>`` for closing the loop
- Any section name with a ``!`` preceding it will not generate the section text (for instance, no text ``Contact`` will appear in the generated resume).
- Using a ``|`` symbol in a section header will use the proceeding text instead of the section name in the outputted resume. So, the final section above will be rendered with a title of ``Mad Skills`` instead of ``Skills``.

Here's a screenshot of the template .docx (you can also find this in the repository_):

.. image:: https://raw.githubusercontent.com/virantha/one_resume/master/images/word_template.png
    :alt: Word resume template
    :width: 679
    :align: center

And, running OneResumé on it will generate the following:

.. image:: https://raw.githubusercontent.com/virantha/one_resume/master/images/word_output.png
    :alt: Word resume output
    :width: 679
    :align: center



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
.. _Mako: http://www.makotemplates.org
.. _repository: https://github.com/virantha/one_resume/blob/master/examples/resume.docx?raw=true
.. |image_pypi| image:: https://badge.fury.io/py/one_resume.png
   :target: https://pypi.python.org/pypi/one_resume
.. |image_downloads| image:: https://pypip.in/d/one_resume/badge.png
   :target: https://crate.io/packages/one_resume?version=latest
.. |image_license| image:: https://pypip.in/license/one_resume/badge.png
.. |passing| image:: https://scrutinizer-ci.com/g/virantha/one_resume/badges/build.png?b=master
.. |quality| image:: https://scrutinizer-ci.com/g/virantha/one_resume/badges/quality-score.png?b=master
.. |Coverage Status| image:: https://coveralls.io/repos/virantha/one_resume/badge.png?branch=develop
   :target: https://coveralls.io/r/virantha/one_resume
