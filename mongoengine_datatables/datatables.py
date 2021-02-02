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

    def __init__(self, document, collection):
        super().__init__(document, collection)
        self._dt_columns = None
        self._dt_terms_without_colon = None
        self._dt_limit = None
        self._dt_terms_with_colon = None
        self._dt_custom_filter = None
        self._dt_order_column = None
        self._dt_order_direction = None
        self._dt_data = None

    @property
    def _dt_global_search(self):
        and_filter = [
            {
                "$or": [
                    {column: {"$regex": term, "$options": "i"}}
                    for column in self._dt_columns
                ]
            }
            for term in self._dt_terms_without_colon
        ]
        return {"$and": and_filter} if and_filter else {}

    @property
    def _dt_column_search(self):
        column_search = dict()
        for term in self._dt_terms_with_colon:
            col, term = term.split(":")
            column_search.update({col: {"$regex": term, "$options": "i"}})
        return column_search

    @property
    def _dt_aggregate(self):
        match = dict()
        match.update(self._dt_global_search)
        match.update(self._dt_column_search)
        match.update(self._dt_custom_filter)
        projection = {key: {"$ifNull": ["$" + key, ""]} for key in self._dt_columns}
        pipeline = [
            {"$match": match},
            {"$sort": {self._dt_order_column: self._dt_order_direction}},
            {"$skip": self._dt_data["start"]},
            {"$project": projection},
            {"$limit": self._dt_limit},
        ]
        return list(self.aggregate(pipeline))

    @property
    def _data(self):
        """Clean the aggregate results for DataTables.

        Note that using `json.dumps` on some types means they display properly
        in the table, but you'll have to remove those lines if you want to access
        an embedded key like `key.embedded_key`.

        """
        data_out = self._dt_aggregate
        for d in data_out:
            d["DT_RowId"] = str(d.pop("_id"))
            for key, val in d.items():
                if type(val) in [list, dict, float]:
                    d[key] = json.dumps(val, default=str)
        return data_out

    def datatables(self, data, **custom_filter):
        """Method to get results for DataTables.

        Args:
            data (dict): The data as sent by DataTables' server-side ajax call.
            **custom_filter: A dict of key/val pairs for injecting to MongoDB search.

        Returns:
            dict with data and meta required by DataTables.

        """
        self._dt_custom_filter = custom_filter
        self._dt_data = data
        self._dt_columns = [column["data"] for column in data["columns"]]
        self._dt_limit = None if data["length"] == -1 else data["length"]
        self._dt_order_direction = {"asc": 1, "desc": -1}[data["order"][0]["dir"]]
        self._dt_order_column = self._dt_columns[data["order"][0]["column"]]
        search_terms = data["search"]["value"].split()
        self._dt_terms_with_colon = [
            term for term in search_terms if term.count(":") == 1
        ]
        self._dt_terms_without_colon = [
            term for term in search_terms if term.count(":") != 1
        ]

        return {
            "recordsTotal": str(self.count()),
            "recordsFiltered": str(len(self._data)),
            "draw": int(data["draw"]),
            "data": self._data,
        }
