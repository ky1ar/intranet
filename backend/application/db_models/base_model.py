from application import db


class BaseModel(db.Model):
    __abstract__ = True

    def to_dict(self, only_fields=None, exclude_fields=None):
        if only_fields:
            only_fields = set(only_fields)
        if exclude_fields:
            exclude_fields = set(exclude_fields)

        result = {}
        for column in self.__table__.columns:
            if only_fields and column.name not in only_fields:
                continue
            if exclude_fields and column.name in exclude_fields:
                continue
            result[column.name] = getattr(self, column.name)

        return result