from formencode import Schema, All, validators

from datahub.exc import NotFound
from datahub.model import Node, Account

from datahub.logic.search import index_add
from datahub.logic.validation import Name, AvailableNodeName

class NodeSchemaState():
    """ Used to let the AvailableNodeName validator know that the 
    current name is taken by the resource itself. """

    def __init__(self, owner_name, current_name):
        self.owner_name = owner_name
        self.current_name = current_name

class NodeSchema(Schema):
    allow_extra_fields = True
    name = All(Name(not_empty=True), AvailableNodeName())
    summary = validators.String(min=0, max=3000, if_missing='',
                                if_empty='')

def get(owner_name, node_name):
    """ Get will try to find a node and return None if no resource is
    found. Use `find` for an exception-generating variant. """
    return Node.query.join(Node.owner).\
            filter(Account.name==owner_name).\
            filter(Node.name==node_name).first()

def find(owner_name, node_name):
    """ Find a node or yield a `NotFound` exception. """
    resource = get(owner_name, node_name)
    if resource is None:
        raise NotFound('No such resource: %s / %s' % (owner_name, 
                       node_name))
    return resource

def rebuild():
    """ Rebuild the search index for all nodes. """
    for node in Node.query:
        index_add(node)