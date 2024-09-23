=====
Usage
=====


To use cheflib in a project:

.. code-block:: python

    from cheflib import Chef
    userid = 'dummy_user'
    chef_url = 'some url to the chef server...'
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
