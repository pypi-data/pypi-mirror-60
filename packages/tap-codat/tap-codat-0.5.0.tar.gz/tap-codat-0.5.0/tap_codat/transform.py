import pendulum
from singer.utils import strftime as singer_strftime


class DictKey(object):
    expected_type = dict
    def __init__(self, key):
        self.key = key
    def __repr__(self):
        return "<DictKey({})>".format(self.key)
    def __eq__(self, other):
        return self.key == other.key
    def iterate(self, item):
        yield self.key, item.get(self.key)


class _ListItems(object):
    expected_type = list
    def __repr__(self):
        return "<ListItems>"
    def iterate(self, item):
        for i, v in enumerate(item):
            yield i, v

ListItems = _ListItems()


def find_dt_paths(schema, path=None):
    """Given a schema, recursively finds all keys with a date-time format.

    Returns a list of lists, where each inner list represents the path in a
    record where a date-time would be found. For example, if the path were

        [DictKey("foo"), ListItems, DictKey("bar")]

    Then for a record matching this schema, a date-time value could be found
    with:

        record["foo"][0]["bar"]

    Note that ListItems is used to indicate there will be a list, rather than a
    dict. Hence if the path were

        [ListItems]

    This means that all items inside the list are date-times."""
    path = path or []
    found = []
    if schema.format == "date-time":
        found.append(path)
    elif schema.properties:
        for k, v in schema.properties.items():
            found += find_dt_paths(v, path + [DictKey(k)])
    elif schema.items:
        found += find_dt_paths(schema.items, path + [ListItems])
    return found


class TransformationException(Exception):
    def __init__(self, item, path, path_idx):
        super().__init__(
            "item type {}; path {}; path_idx {}"
            .format(type(item), path, path_idx)
        )

def _check_type(item, path, path_idx):
    path_item = path[path_idx]
    if not isinstance(item, path_item.expected_type):
        raise TransformationException(item, path, path_idx)


def safe_strftime(dt):
    # Different implementations of the C strftime lib
    # will render out years differently. This function
    # tries to use the Singer strftime func, then falls
    # back to a different implementation.
    #
    # If the strftime lib is different than the expected version,
    # then the resulting date will look like
    #
    # 4Y-01-01 12:00:00...
    #
    # This code catches this failure mode, and use an alternative fmt string

    res = singer_strftime(dt)
    if res.startswith('4Y'):
        res = dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    return res

def _transform_impl(item, path, path_idx=0):
    if not item:
        return item
    if path_idx == len(path):
        dt = pendulum.parse(item).in_timezone("UTC")
        return safe_strftime(dt)
    _check_type(item, path, path_idx)
    path_item = path[path_idx]
    for k, v in path_item.iterate(item):
        if not v:
            continue
        item[k] = _transform_impl(v, path, path_idx + 1)
    return item


def transform_dts(records, paths):
    """Accepts a list of records and a list of paths and re-formats all
    date-times to RFC3339.

    `paths` is a list as output by the `find_dt_paths` function."""
    for path in paths:
        _transform_impl(records, [ListItems] + path)
    return records
