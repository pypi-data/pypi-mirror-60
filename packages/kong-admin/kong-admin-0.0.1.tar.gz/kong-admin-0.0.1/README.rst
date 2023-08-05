kong-admin
================

A kong admin api sdk.

安装
-----

.. code-block:: sh

    pip install kong-admin


使用
------

.. code-block:: python

    from kong_admin import KongAdmin

    host = "http:://localhost:8001"
    ka = KongAdmin(host=host)
    r = ka.get("/consumers")
    print(r.json())
