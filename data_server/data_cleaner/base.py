from typing import Dict, List

from django.db.models import Model
from django.db.models.query import QuerySet


class QS:
    def get_queryset(self, qs: QuerySet):
        raise NotImplementedError


class DeleteQueryset(QS):
    pass


class ExcludeQueryset(QS):
    pass


class DataCleaner:
    start_queryset: QuerySet = None
    delete_queryset_list: List[DeleteQueryset] = []
    exclude_queryset_list: List[ExcludeQueryset] = []
    model: Model = None

    '''
    delete queryset중 남겨야 하는 데이터 수
    ex) value = 50, queryset.count = 200 -> 150개만 삭제
    ex) value = 50, queryset.count = 30 -> 삭제하지 않음
    '''
    remain_delete_count: int = 0

    '''
    데이터 중요도에 따른 정렬
    우선 순위가 낮은 것 부터 삭제됨
    '''
    ordering: List[str] = []

    def __init__(self):
        for qs in self.delete_queryset_list:
            if not isinstance(qs, DeleteQueryset):
                raise Exception
        for qs in self.exclude_queryset_list:
            if not isinstance(qs, ExcludeQueryset):
                raise Exception

    def clean(self) -> None:
        qs = self.get_final_queryset()
        self.write_log(*qs.delete())

    @classmethod
    def write_log(cls, deleted: int, detail: Dict[str, int]) -> None:
        log = f'{cls}에 의해 {deleted}개의 데이터가 삭제되었습니다. {detail}'
        print(log)

    def get_final_queryset(self) -> QuerySet[model]:
        delete_queryset = self.get_delete_queryset()
        exclude_queryset = self.get_exclude_queryset()
        res = delete_queryset.difference(exclude_queryset).order_by(*self.ordering)[self.remain_delete_count:]
        return self.refresh_queryset(res)

    def refresh_queryset(self, qs: QuerySet[model]) -> QuerySet[model]:
        ids = set(row.id for row in qs)
        return self.start_queryset.filter(id__in=ids)

    def get_delete_queryset(self) -> QuerySet[model]:
        return self.union_queryset_list(self.delete_queryset_list)

    def get_exclude_queryset(self) -> QuerySet[model]:
        return self.union_queryset_list(self.exclude_queryset_list)

    def union_queryset_list(self, queryset_list: List[QS]) -> QuerySet[model]:
        res = queryset_list[0].get_queryset(self.start_queryset)
        for qs in queryset_list:
            res = res.union(qs.get_queryset(self.start_queryset))
        return res
