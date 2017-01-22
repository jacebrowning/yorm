from yorm import utilities


class ModelMixin:
    """Adds ORM methods to a mapped class."""

    @classmethod
    def new(cls, *args, **kwargs):
        return utilities.create(cls, *args, **kwargs)

    @classmethod
    def find(cls, *args, **kwargs):
        return utilities.find(cls, *args, **kwargs)

    @classmethod
    def match(cls, *args, **kwargs):
        return utilities.match(cls, *args, **kwargs)

    def load(self):
        return utilities.load(self)

    def save(self):
        return utilities.save(self)

    def delete(self):
        return utilities.delete(self)
