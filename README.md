# MongoEngine DataTables

The `DataTablesManager` class can be used instead of the default MongoEngine
`QuerySet` class to add a `datatables` method for returning results as required by the
jQuery plugin DataTables.

## Installation
 
    pip install git+git://github.com/pauljolsen/mongoengine-datatables.git@v0.1.2
    

## Example

Here's an example for Flask.
    
#### models.py

    from mongoengine import Document, StringField, ListField
    from mongoengine_datatables import DataTablesManager
    

    class Links(Document):
        """The MongoEngine ODM class for the links_links collection."""
    
        meta = {
            "collection": "links_links",
            "queryset_class": DataTablesManager
        }
        name = StringField()
        category = StringField()
        link = StringField()
        group = ListField()


#### routes.py

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


#### app.js

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
