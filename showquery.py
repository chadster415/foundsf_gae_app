from google.appengine.ext import db
from google.appengine.api import datastore

def showQuery(query):
    """Represent a query as a string"""
    kind = query._model_class.kind()
    ancestor = query._Query__ancestor
    filters = query._Query__query_set
    orderings = query._Query__orderings
    hint = None
    limit = None
    offset = None

    res = ["%s.all()" % kind]
    if ancestor is not None:
        res.append("ancestor(%r)" % ancestor)
    for k in sorted(filters):
        res.append("filter(%r, %r)" % (k, filters[k]))
    for p, o in orderings:
        if o==datastore.Query.DESCENDING:
            p = '-'+p
        res.append("order(%r)" % p)

    return '.'.join(res)

def showGqlQuery(query):
    """Represent a GQL query as a string"""
    proto = query._proto_query
    kind = query._model_class.kind()
    filters = proto.filters()
    boundfilters = proto._GQL__bound_filters
    orderings = proto.orderings()
    hint = proto.hint()
    limit = proto.limit()
    offset = proto._GQL__offset

    select = "SELECT * FROM %s" % kind
    where = []
    order = []

    for k in sorted(filters):
        for clause in filters[k]:
            name, op = clause
            if name==-1: name = 'ANCESTOR'
            where.append("%s %s :%s" % (name, op.upper(), k))

    for k in sorted(boundfilters):
        if isinstance(k, tuple):
            op = ' '.join(k)
        else:
            op = k
        where.append("%s %r" % (op, boundfilters[k]))

    for p, o in orderings:
        order.append("%s %s" % (p, 'DESC' if o==datastore.Query.DESCENDING else 'ASC'))

    gql = select
    if where:
        gql += ' WHERE '+' AND '.join(where)
    if order:
        gql += ' ORDER BY ' + ', '.join(order)
    if limit != -1:
        if offset != -1:
            gql += ' LIMIT %s,%s' % (offset,limit)
        else:
            gql += ' LIMIT %s' % limit
    elif offset != -1:
            gql += ' OFFSET %s' % offset
    return gql