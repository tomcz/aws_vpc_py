Attempt to create an Amazon VPC using python tools
==================================================

Requirements
------------

You should not need to do anything special except to invoke the `./go` script.
It should do the rest including setting up the required python libraries in a virtualenv environment.

Notes
-----

* These scripts have been written for Python 2.7.2 and may not work with other versions.
* EC2 scripts additionally require both [boto](http://docs.pythonboto.org/en/latest/)
  and [fabric](http://docs.fabfile.org/en/1.5/) in order to provision and control
  multiple EC2 instances.

License
-------

These scripts are covered by the [MIT License](http://www.opensource.org/licenses/mit-license.php).
