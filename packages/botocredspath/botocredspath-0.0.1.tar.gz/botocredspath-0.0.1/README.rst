botcredspath
============

because Boto3 should allow you to set the path to your `~/.aws` file without envars, but it doesn't (at least not that I can tell).

usage
========

.. code-block:: python

    import boto3_creds_path as bcp
    import boto3

    boto3=bcp.update_path(boto3,'/absolute/path/to/files') ## this replaces /.aws

    client=boto3.client('s3') # now use boto3 like normal reading from the new path
