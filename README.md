# DataTables with MongoEngine

The `DataTablesManager` class can be used instead of the default MongoEngine
`QuerySet` class to add a `datatables` method for returning results as required by the
jQuery plugin DataTables.

> Performance Issues
> I have seen performance issues with this for large collections. The mongo-datatables package performs much better!

## Installation
 
    pip install datatables-mongoengine
    

## Example

Here's an example for Flask.
    
### models.py

    from mongoengine import Document, StringField, ListField
    from datatables_mongoengine import DataTablesManager
    

    class Links(Document):
        """The MongoEngine ODM class for the links collection."""
    
        meta = {
            "queryset_class": DataTablesManager
        }
        name = StringField()
        category = StringField()
        link = StringField()
        group = ListField()


### routes.py

    from flask import request, g, jsonify
    
    from app import app
    from app.models import Links
    
    
    @app.route("/ajax/links", methods=["POST"])
    def ajax_links():
        """Get results from MongoDB for DataTables."""
        
        data = request.get_json()
        custom_filter = {
            'group': g.user.group
        }
        
        results = Links.objects.datatables(data, **custom_filter)
        return jsonify(results)

Note that you can inject any filter you want server-side, like I do above to make sure
the results all match the current user's group.


### app.js

    $(document).ready( function () {
        $('#example').DataTable({
            processing: true,
            serverSide: true,
            ajax: {
                url: '/ajax/links',
                dataSrc: 'data',
                type: 'POST',
                contentType: 'application/json',
                data: function (d) {
                    return  JSON.stringify(d)
                }
            },
            columns: [
                { data: 'name'},
                { data: 'category'},
                { data: 'link'}
            ],
        });


### A note about flask-mongoengine

If you're using flask-mongoengine but overriding the default QuerySet class like above,
you'll lose a few nice things like the `get_or_404` method, which works like Django's 
`get_object_or_404`. You can add that back (and more), like this.

    
    from flask import jsonify, abort, make_response
    from mongoengine import DoesNotExist
    from datatables_mongoengine import DataTablesManager
    

    class MyQuerySet(DataTablesManager):
        """Some tricks from flask-mongoengine that we miss."""

        def get_or_404(self, *args, **kwargs):
            """Get a document and raise a 404 Not Found error if it doesn't exist."""
            try:
                return self.get(*args, **kwargs)
            except DoesNotExist:
                abort(404)
    
        def get_or_json_404(self, *args, **kwargs):
            """
            Same as above but with a JSON response. This doesn't come from 
            flask-mongoengine.
            """
            try:
                return self.get(*args, **kwargs)
            except DoesNotExist:
                abort(make_response(jsonify(message="Not found"), 404))
    
        def first_or_404(self):
            """Same as get_or_404, but uses .first, not .get."""
            obj = self.first()
            if obj is None:
                abort(404)
            return obj
            
Now set `queryset_class` to `MyQuerySet` and you can again do 
`Model.objects.get_or_404(key="val")`.  There's also a `paginate` method created by
flask-mongoengine but I haven't used it so I'm excluding it.
