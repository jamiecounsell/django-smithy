=====
Usage
=====

Before sending requests, you must first create a blueprint. Request blueprints drive all the requests sent through Django Smithy.

Once a blueprint is created, you can call the :code:`send` method and provide a dictionary of context. This context will be passed to all properties of the request and interpreted using Django's template language.

Django template syntax is supported in pretty much everything, including the name and value of headers, cookies, and query parameters, as well as the request body and URL. This makes it easy to make dynamic requests that contain contextual data.

Variables are just static values that allow you to easily reuse or swap out data without needing to provide it in code. This is great for storing things like API keys, but it's important to note the security impacts of this, as the API key will be visible in plain text to any user with access to this section of the Django Admin.

.. code-block:: python

    # Retrieve the blueprint
    # (will change depending on your use case)
    blueprint = RequestBlueprint.objects.first()

    # Send the request and get the record
    record = blueprint.send(context = {
        'something': 'some value',
        'more_stuff': 0
    })

    # Or get all records for that blueprint
    RequestRecord.from_blueprint(blueprint)

Once sent, a request will generate a RequestRecord with details of the response. The RequestRecord can be used to determine if a request failed or not and handle appropriately.
