# -*- coding: utf-8 -*-
###############################################################################
# NSAp - Copyright (C) CEA, 2019 - 2020
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
###############################################################################


"""
This module provides tools to generate/request an ElasticSearch filesystem
reference.
"""

# Imports
from collections import OrderedDict
from pprint import pprint
import time
import ssl
import progressbar
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, parallel_bulk
from elasticsearch.connection import create_ssl_context


class Blizzard(object):
    """ This class enables us to construct a filesystem resource with
    ElasticSearch.
    """

    def __init__(self, url, verify_certs=True):
        """ Initialize the Blizzard class.

        Use the bulk API to perform many index operations in a single API call.
        This can greatly increase the indexing speed.

        Parameters
        ----------
        url: str
            the server url.
        verify_certs: bool, default True
            verify server certificate.
        """
        kwargs = {}
        if not verify_certs:
            ssl_context = create_ssl_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            kwargs["verify_certs"] = verify_certs
            kwargs["ssl_context"] = ssl_context
        self.session = Elasticsearch([url], **kwargs)

    @classmethod
    def _format_result(cls, res):
        """ Format the result of a query.

        Parameters
        ----------
        res: dict
            the returned query result.

        Returns
        -------
        format_res: dict
            the formated returned query result.
        """
        format_res = dict((item["_id"], item["_source"])
                          for item in res["hits"]["hits"])
        return format_res

    def _scroll(self, data):
        """ Use the scroll API to retrieve the result of a query.

        Parameters
        ----------
        data: dict
            the returned query data.

        Returns
        -------
        format_res: dict
            the formated returned query result.
        """
        scroll_id = data["_scroll_id"]
        scroll_size = len(data["hits"]["hits"])
        scroll_result = {}
        while scroll_size > 0:
            scroll_result.update(Blizzard._format_result(data))
            data = self.session.scroll(scroll_id=scroll_id, scroll="1m")
            scroll_id = data["_scroll_id"]
            scroll_size = len(data["hits"]["hits"])
        return scroll_result

    ###########################################################################
    #   Public Methods
    ###########################################################################

    def add_mapping(self, index, mapping):
        """ Create an index and add an index.

        Parameters
        ----------
        index: str
            the index name.
        mapping: dict
            the index mapping.
        """
        self.session.indices.create(index=index, ignore=400, body=mapping)

    def status(self, full=False, display=True):
        """ Display the content status.

        Parameters
        ----------
        full: bool, default False
            if True display the ElasticSearch cluster sttatus.
        display: bool, default True
            if True display the status.

        Returns
        -------
        result: dict
            the ElasticSearch current status.
        """
        query = {"query": {"match_all": {}}}
        result = OrderedDict()
        if full:
            for key, val in self.session.info().items():
                result[key] = val
        for index in self.session.indices.get_alias().keys():
            status = self.session.count(index=index, body=query)
            result[index] = status["count"]
            if index == "timestamp":
                _query = {"size": 10000, "query": {"match_all": {}}}
                status = Blizzard._format_result(
                    self.session.search(index=index, body=_query))
                for key, val in status.items():
                    result[val["project"]] = val["timestamp"]
        if display:
            print("-" * 20)
            for key, val in result.items():
                if not isinstance(val, int):
                    print("       {0:15}  {1}".format(key, val))
                else:
                    print("- {0:20}: {1}".format(key, val))
            print("-" * 20)
        return result

    def list(self, path):
        """ List the content of the input path.

        Parameters
        ----------
        path: str
            the path to be listed.

        Returns
        -------
        data: list
            the path content.
        """
        query = {
            "size": 10000,
            "query": {
                "term": {
                    "path": path
                }
            }
        }
        data = self.session.search(
            index="content", body=query, request_timeout=500, scroll="1m")
        result = self._scroll(data)
        if path not in result:
            print("'{0}' is not defined.".format(path))
            return []
        return result[path]["ls"]
            

    def search(self, keys=None):
        """ Retrieve the files that matche the filtering keys.

        Parameters
        ----------
        keys: list of str, default None
            the filtering keys.

        Returns
        -------
        data: list
            the requested files.
        """
        if keys is None:
            query = {
                "query": {
                    "size": 10000,
                    "match_all": {}
                }
            }
        else:
            query = {
                "size": 10000,
                "query": {
                    "match": {
                        "keys": {
                            "operator": "and",
                            "query": " ".join(keys)
                        }
                    }
                }
            }
        data = self.session.search(
            index="files", body=query, request_timeout=500, scroll="1m")
        result = self._scroll(data)
        return list(result.keys())

    def import_data(self, actions, thread_count=1):
        """ Method that import one chromsome data in the database.

        Parameters
        ----------
        actions: dict
            some bulk data to be inserted.
        thread_count: int, default 1
            size of the threadpool to use for the bulk requests.
        """
        chunk_size = 50000
        if thread_count == 1:
            result = bulk(self.session, actions, chunk_size=chunk_size,
                          stats_only=True, request_timeout=500)
            print(result)
        else:
            parallel_bulk(self.session, actions, thread_count=thread_count,
                          chunk_size=chunk_size)

    def delete_index(self, name):
        """ Delete a specific index.

        Parameters
        ----------
        name: str
            the name of the index to be deleted.
        """
        self.session.indices.delete(index=name, ignore=[400, 404])

