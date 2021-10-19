from django.db import models
from raw_data.exceptions import JsonDataAlreadyExist


class BaseManager(models.Manager):
    def create_from_json(self, json_data_obj, **kwargs):
        kwargs['json'] = json_data_obj
        kwargs.update(self.model.parse_json(json_data_obj.dot_data))
        return self.create(**kwargs)

    def create_or_get_from_api(self, **kwargs):
        api = self.model.api_call_class(**kwargs)
        try:
            json_data_obj = api().save_to_db()
        except JsonDataAlreadyExist:
            return self.model.objects.get(json=api.json_data_obj)
        return self.create_from_json(json_data_obj)

    def creates_or_get_from_api(self, **kwargs):
        pk_list = []
        keys = kwargs.keys()
        values = kwargs.values()

        for val_list in zip(*values):
            api_params = {key: val for key, val in zip(keys, val_list)}
            obj = self.create_or_get_from_api(**api_params)
            pk_list.append(obj.pk)

        return self.model.objects.filter(pk__in=pk_list)


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = BaseManager()

    class Meta:
        abstract = True

    @classmethod
    def parse_json(cls, dot_json_data):
        prefix = 'parse_'
        dic = {}

        for attr in dir(cls):
            if not attr.startswith(prefix) or attr == 'parse_json':
                continue

            method = getattr(cls, attr)
            field_name = attr.split(prefix)[1]
            dic[field_name] = method(dot_json_data)

        return dic
