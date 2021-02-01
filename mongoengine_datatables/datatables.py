"""
The DataTablesManager class can be used instead of the default MongoEngine
QuerySet class to add a `datatables` method for returning results as required by the
jQuery plugin DataTables.

Usage:
    Machine.objects.datatables(data=request.get_json(), Group=g.user.group)

"""

import json
from mongoengine import QuerySet


class DataTablesManager(QuerySet):
    """Mixin for connecting DataTables to MongoDB with MongoEngine."""

    def datatables(self, data, **custom_filter):
        """Method to get results for DataTables.

        Args:
            data (dict): The data as sent by DataTables' server-side ajax call.
            stringify (list): List of types to json.dumps
            **custom_filter: A dict of key/val pairs for injecting to MongoDB search.

        Returns:
            dict with data and meta required by DataTables. Note it doesn't return
            a QuerySet, which might be breaking some MongoEngine rules.
        """
        columns = [column["data"] for column in data["columns"]]
        limit = None if data["length"] == -1 else data["length"]
        order_direction = {"asc": 1, "desc": -1}[data["order"][0]["dir"]]
        order_column = columns[data["order"][0]["column"]]
        search_terms = data["search"]["value"].split()
        terms_with_colon = [term for term in search_terms if term.count(":") == 1]
        terms_without_colon = [term for term in search_terms if term.count(":") != 1]
        projection = {key: {"$ifNull": ["$" + key, ""]} for key in columns}

        # Build the global search--a list comprehension within a list comprehension
        and_filter = [
            {"$or": [{column: {"$regex": term, "$options": "i"}} for column in columns]}
            for term in terms_without_colon
        ]
        global_search = {"$and": and_filter} if and_filter else {}

        # Build the specific column search
        column_search = dict()
        for term in terms_with_colon:
            col, term = term.split(":")
            column_search.update({col: {"$regex": term, "$options": "i"}})

        # Build the match filter
        match = dict()
        match.update(global_search)
        match.update(column_search)
        match.update(custom_filter)

        # Build the aggregation pipeline
        pipeline = [
            {"$match": match},
            {"$sort": {order_column: order_direction}},
            {"$skip": data["start"]},
            {"$project": projection},
            {"$limit": limit},
        ]

        # Query for results
        data_out = list(self.aggregate(pipeline))
        for d in data_out:
            d["DT_RowId"] = str(d.pop("_id"))

            # This is optional but lets these types display properly.
            # Comment if you want to access an embedded key like `key.embedded_key`.
            for key, val in d.items():
                if type(val) in [list, dict, float]:
                    d[key] = json.dumps(val, default=str)

        return {
            "recordsTotal": str(self.count()),
            "recordsFiltered": str(len(data_out)),
            "draw": int(data["draw"]),
            "data": data_out,
        }
