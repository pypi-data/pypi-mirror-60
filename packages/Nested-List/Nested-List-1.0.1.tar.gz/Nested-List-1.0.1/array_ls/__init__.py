"""
A package that operates on a list whose type of element is list or tuple.
It's built based on the operator.itemgetter.
"""
from operator import itemgetter


def sort(dl, order=False, *keys):
    dl.sort(key=itemgetter(*keys), reverse=order if order is True or order == "DESC" else False)


def delete_items(dl, compare, indexes, values):
    get_values = itemgetter(*indexes)
    for d in dl:
        if compare == 'L' and get_values(d) <= values:
            dl.remove(d)
        elif compare == 'G' and get_values(d) >= values:
            dl.remove(d)
        elif get_values(d) == values:
            dl.remove(d)


def max(dl, *keys):
    return dl.max(key=itemgetter(*keys))


def min(dl, *keys):
    return dl.min(key=itemgetter(*keys))
