============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

Submit Feedback
~~~~~~~~~~~~~~~

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.


To develop on cheflib, we made a set op scripts available to help you out:

.. code-block:: bash

    # The following commands require pipenv as a dependency

    # To lint the project
    _CI/scripts/lint.py

    # To execute the testing
    _CI/scripts/test.py

    # To create a graph of the package and dependency tree
    _CI/scripts/graph.py

    # To build a package of the project under the directory "dist/"
    _CI/scripts/build.py

    # To see the package version
    _CI/scripts/tag.py

    # To bump semantic versioning [--major|--minor|--patch]
    _CI/scripts/tag.py --major|--minor|--patch

    # To upload the project to a pypi repo if user and password are properly provided
    _CI/scripts/upload.py

    # To build the documentation of the project
    _CI/scripts/document.py


Get Started!
------------

Ready to contribute? Here's how to set up `cheflib` for local development.
Using of pipenv is highly recommended.

1. Clone your fork locally::

    $ git clone https://github.com/schubergphilis/cheflib.git

2. Install your local copy into a virtualenv. Assuming you have pipenv installed, this is how you set up your clone for local development::

    $ cd cheflib/
    $ pipenv install --ignore-pipfile

3. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.
   Do your development while using the CI capabilities and making sure the code passes lint, test, build and document stages.


4. Commit your changes and push your branch to the server::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

5. Submit a merge request
