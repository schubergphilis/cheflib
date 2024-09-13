=====
Usage
=====


To develop on cheflib:

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


To use cheflib in a project:

.. code-block:: python

    from cheflib import Chef
    userid = 'dummy_user'
    chef_url = 'https://chef.example.com'
    organization = 'dummy_org'
    private_key_contents = 'Private RSA Key contents here...'
    chef = Chef(chef_url, organization, userid, private_key_contents)
    n = chef.create_node('dummy_node')
    n.normal = {'ipaddress': '1.1.1.1'}

    # get node by name or IP address
    n = chef.get_node_by_name('dummy_node')
    n = chef.get_node_by_ip_address('1.1.1.1')

    # full search, will return all node attributes
    nodes = chef.search_nodes('name:dummy*')
    for n in nodes:
        print(n.data)

    # partial search, will return only requested attributes
    keys = {
        "name": ["name"],
        "ip": ["ipaddress"],
        "kernel_version": ["kernel", "version"]
    }

    nodes = chef.search_nodes('name:dummy*', keys=keys)
    for n in nodes:
        print(n.data)

    # delete node
    chef.delete_node_by_name('dummy_node')

    # or

    n = chef.get_node_by_name('dummy_node')
    n.delete()
