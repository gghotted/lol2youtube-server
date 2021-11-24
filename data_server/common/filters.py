from typing import Any, Tuple

from django.contrib.admin import SimpleListFilter


def AnnotateFieldFilterFactory(field: str, values_list: Tuple[Any]):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{field: self.value()})

    def lookups(self, request, model_admin):
        return [(value, str(value)) for value in values_list]

    newclass = type(field + 'AnnotateFieldFilter', (SimpleListFilter, ), {'queryset': queryset, 'lookups': lookups})
    newclass.title = field
    newclass.parameter_name = field
    return newclass
