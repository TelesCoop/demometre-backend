from rest_framework import serializers


class FilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """
    Restaurant fields are serialized to return their id.
    """

    def __init__(self, **kwargs):
        self.get_queryset_fn = kwargs.pop("get_queryset_fn", None)
        # setattr(self, "get_queryset", kwargs.pop("get_queryset", None))
        super().__init__(**kwargs)

    def get_queryset(self):
        return self.get_queryset_fn(self)
