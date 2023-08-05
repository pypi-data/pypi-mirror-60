import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel
from isc_common.models.tree_audit import TreeAuditModelManager, TreeAuditModelQuerySet
from kaf_pas.planing.models.operations import Operations

logger = logging.getLogger(__name__)


class Operation_refsQuerySet(TreeAuditModelQuerySet):
    def delete(self):
        return super().delete()

    def _check(self, **kwargs):
        if kwargs.get('income') != None:
            if isinstance(kwargs.get('income'), Operations):
                income = kwargs.get('income').id
            else:
                income = kwargs.get('income')

            if isinstance(kwargs.get('outcome'), Operations):
                outcome = kwargs.get('outcome').id
            else:
                outcome = kwargs.get('outcome')

            if income == outcome:
                raise Exception(f'Attempt to write circular reference id ({income})')

    def create(self, **kwargs):
        self._check(**kwargs)
        return super().create(**kwargs)

    def update(self, **kwargs):
        self._check(**kwargs)
        return super().update(**kwargs)

    def get_or_create(self, defaults=None, **kwargs):
        self._check(**kwargs)
        return super().get_or_create(defaults, **kwargs)

    def update_or_create(self, defaults=None, **kwargs):
        self._check(**kwargs)
        return super().update_or_create(defaults, **kwargs)


class Operation_refsManager(TreeAuditModelManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'income': record.income.id if record.income else None,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Operation_refsQuerySet(self.model, using=self._db)


class Operation_refs(AuditModel):
    parent = ForeignKeyProtect(Operations, related_name='operation_parent', blank=True, null=True)
    child = ForeignKeyProtect(Operations, related_name='operation_child')

    objects = Operation_refsManager()

    def __str__(self):
        return f"ID:{self.id}"

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица операций планирования'
