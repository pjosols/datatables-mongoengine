# MongoEngine DataTables

The `DataTablesManager` class can be used instead of the default MongoEngine
`QuerySet` class to add a `datatables` method for returning results as required by the
jQuery plugin DataTables.

#### Installation
 
    pip install git+git://github.com/pauljolsen/mongoengine-datatables.git@v0.1.0
    
    
#### Sample model

    from mongoengine import Document, StringField
    from mongoengine_datatables import DataTablesManager
    

    class Links(Document):
        """The MongoEngine ODM class for the links_links collection."""
    
        meta = {
            "collection": "links_links",
            "strict": False,
            "queryset_class": DataTablesManager
        }
        name = StringField()
        category = StringField()
        link = StringField()


#### Sample route

    from flask import request, g, jsonify
    
    from app.links import links
    from app.links.models import Links
    
    
    @links.route("/ajax/links", methods=["POST"])
    def ajax_links():
        """Get results from MongoDB for DataTables."""
        
        results = Links.objects.datatables(
            data=request.get_json(), 
            Group=g.user.group.name
            )
        return jsonify(results)


#### Sample DataTables

    $(document).ready( function () {
        $('#example').DataTable({
            processing: true,
            serverSide: true,
            ajax: {
                url: '/links/ajax/links',
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