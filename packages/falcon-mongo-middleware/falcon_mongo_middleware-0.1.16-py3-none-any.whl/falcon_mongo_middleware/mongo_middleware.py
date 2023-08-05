import os
from importlib import import_module

from pymongo import MongoClient
server_selection_timeout = int(os.getenv('SERVER_SELECTION_TIMEOUT', 5000))
mongo_uri = os.getenv('MONGODB_URI')
mongo_schema_path = os.getenv('MONGODB_SCHEMA_PATH', 'schemas.collections')


def get_mongodb_client():
    return MongoClient(mongo_uri, serverSelectionTimeoutMS=server_selection_timeout)


def initialize_database(client: MongoClient, customer_guid: str):
    try:
        collections = import_module(mongo_schema_path)
        for collection, config in collections.config.items():
            if 'index_models' in config:
                client[customer_guid][collection].create_indexes(config['index_models'])
    except AttributeError as e:
        # TODO Logging
        print('no index configs found')
    except ModuleNotFoundError as e:
        # TODO Logging
        print('no configuration module found')


class MongoMiddleware(object):
    client = get_mongodb_client()
    databases = set(client.list_database_names())

    def process_request(self, req, resp):
        """Process the request before routing it.

        Note:
            Because Falcon routes each request based on req.path, a
            request can be effectively re-routed by setting that
            attribute to a new value from within process_request().

        Args:
            req: Request object that will eventually be
                routed to an on_* responder method.
            resp: Response object that will be routed to
                the on_* responder.
        """
        pass

    def process_resource(self, req, resp, resource, params):
        """Process the request after routing.

        Note:
            This method is only called when the request matches
            a route to a resource.

        Args:
            req: Request object that will be passed to the
                routed responder.
            resp: Response object that will be passed to the
                responder.
            resource: Resource object to which the request was
                routed.
            params: A dict-like object representing any additional
                params derived from the route's URI template fields,
                that will be passed to the resource's responder
                method as keyword arguments.
        """
        # If it's an options request it's coming from react, don't do anything.
        if req.method != 'OPTIONS':
            customer_guid = req.get_header('CUSTOMER-GUID', required=True)
            # reinitialize client if it's ded somehow
            if not self.client:
                # No default needed for mongodb_uri, client defaults to localhost if it's not set
                self.client = get_mongodb_client()
            # If the db doesn't exist, initialize the collections with indexes
            if customer_guid not in self.databases:
                initialize_database(self.client, customer_guid)
                self.databases.add(customer_guid)
            req.context.client = self.client
            req.context.database = self.client[customer_guid]
            req.context.customer_guid = customer_guid
            # TODO Add transaction handling

    def process_response(self, req, resp, resource, req_succeeded):
        """Post-processing of the response (after routing).

        Args:
            req: Request object.
            resp: Response object.
            resource: Resource object to which the request was
                routed. May be None if no route was found
                for the request.
            req_succeeded: True if no exceptions were raised while
                the framework processed and routed the request;
                otherwise False.
        """
        pass