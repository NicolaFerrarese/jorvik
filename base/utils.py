"""
Utilita' varie.


Include il codice di ConceptQ
https://github.com/yourcelf/django-conceptq

"""
import copy
import operator
from functools import reduce

from django.db import models
from django.db.models import Q, F


def is_list(x):
    """
    Controlla se un oggetto e' una lista o meno.
    :param x: L'oggetto da controllare.
    :return: True se x e' una lista, False altrimenti.
    """
    return isinstance(x, list)


def prefix(accessor, q):
    """
    Take a Q object, and prefix its keys so that it can be used from a related
    model.  Also prefixes F expressions.
    Example:
    >>> from django.db.models import Q
    >>> prefix("mailing", Q(sent__isnull=True))
    u"(AND: ("mailing__sent__isnull", True))"
    """
    q = copy.deepcopy(q)
    return _prefix_q(accessor, q, None, None)

def _prefix_q(accessor, q, parent, index):
    if isinstance(q, Q):
        for i, child in enumerate(q.children):
            _prefix_q(accessor, child, q.children, i)
    elif parent is not None and index is not None:
        (k, v) = q
        if isinstance(v, F):
            v = F("__".join(a for a in (accessor, v.name) if a))
        parent[index] = ("__".join(a for a in (accessor, k) if a), v)
    return q

def concept(method):
    """
    This is a decorator for methods on Django manager classes.  It expects the
    method to return a single Q object; however, once decorated, straight calls
    of the method will wrap the Q in a filter to return a queryset.

    -- Modified to work both on Managers and Models.
    """
    def func(self, *args, **kwargs):
        q = method(self, *args, **kwargs)
        if hasattr(self, 'objects'):
            qs = self.objects.filter(q)
        else:
            qs = self.filter(q)
        qs.q = q
        qs.via = lambda accessor: prefix(accessor, q)
        return qs
    return func

from autoslug.settings import slugify as default_slugify
def sede_slugify(value):
    """
    Utilizzato come funzione per la slugifyazione delle sedi
    """
    parole_vietate = ('comitato', 'di', 'della', 'del', 'in', 'provinciale',
                      'locale', 'territoriale', 'regionale', 'nazionale',)
    value = value.replace('d\'', '').replace('D\'', '')
    stringa = default_slugify(value)
    for parola in parole_vietate:
        stringa = stringa.replace(parola + str("-"), "")
    return stringa


def filtra_queryset(queryset, termini_ricerca, campi_ricerca=[]):
        """
        Returns a tuple containing a queryset to implement the search,
        and a boolean indicating if the results may contain duplicates.
        """
        def construct_search(field_name):
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        if termini_ricerca and termini_ricerca:
            orm_lookups = [construct_search(str(search_field))
                           for search_field in campi_ricerca]
            for bit in termini_ricerca.split():
                or_queries = [models.Q(**{orm_lookup: bit})
                              for orm_lookup in orm_lookups]
                queryset = queryset.filter(reduce(operator.or_, or_queries))

        return queryset


def remove_none(obj):
    """
    Rimuove riorsivamente gli elementi None da una lista, tupla o insieme.
    :param obj:
    :return:
    """
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(remove_none(x) for x in obj if x is not None)
    elif isinstance(obj, dict):
        return type(obj)((remove_none(k), remove_none(v)) for k, v in obj.items() if k is not None and v is not None)
    else:
        return obj
