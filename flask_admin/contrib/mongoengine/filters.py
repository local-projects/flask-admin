from flask.ext.admin.babel import gettext
from flask.ext.admin.model import filters
from bson.objectid import ObjectId
from .tools import parse_like_term


class BaseMongoEngineFilter(filters.BaseFilter):
    """
        Base MongoEngine filter.
    """
    def __init__(self, column, name, options=None, data_type=None):
        """
            Constructor.

            :param column:
                Model field
            :param name:
                Display name
            :param options:
                Fixed set of options. If provided, will use drop down instead of textbox.
            :param data_type:
                Client data type
        """
        super(BaseMongoEngineFilter, self).__init__(name, options, data_type)

        self.column = column


# Common filters
class FilterEqual(BaseMongoEngineFilter):
    def apply(self, query, value):
        flt = {'%s' % self.column.name: value}
        return query.filter(**flt)

    def operation(self):
        return gettext('equals')


class FilterNotEqual(BaseMongoEngineFilter):
    def apply(self, query, value):
        flt = {'%s__ne' % self.column.name: value}
        return query.filter(**flt)

    def operation(self):
        return gettext('not equal')


class FilterLike(BaseMongoEngineFilter):
    def apply(self, query, value):
        term, data = parse_like_term(value)
        flt = {'%s__%s' % (self.column.name, term): data}
        return query.filter(**flt)

    def operation(self):
        return gettext('contains')


class FilterNotLike(BaseMongoEngineFilter):
    def apply(self, query, value):
        term, data = parse_like_term(value)
        flt = {'%s__not__%s' % (self.column.name, term): data}
        return query.filter(**flt)

    def operation(self):
        return gettext('not contains')


class FilterGreater(BaseMongoEngineFilter):
    def apply(self, query, value):
        flt = {'%s__gt' % self.column.name: value}
        return query.filter(**flt)

    def operation(self):
        return gettext('greater than')


class FilterSmaller(BaseMongoEngineFilter):
    def apply(self, query, value):
        flt = {'%s__lt' % self.column.name: value}
        return query.filter(**flt)

    def operation(self):
        return gettext('smaller than')


# Customized type filters
class BooleanEqualFilter(FilterEqual, filters.BaseBooleanFilter):
    def apply(self, query, value):
        flt = {'%s' % self.column.name: value == '1'}
        return query.filter(**flt)


class BooleanNotEqualFilter(FilterNotEqual, filters.BaseBooleanFilter):
    def apply(self, query, value):
        flt = {'%s' % self.column.name: value != '1'}
        return query.filter(**flt)

class FilterObjectIdEqual(BaseMongoEngineFilter):
    def apply(self, query, value):
        column_name = self.column.name

        flt = {'%s' % column_name: value}
        return query.filter(**flt)

    def operation(self):
        return gettext('ObjectId equal')

class FilterObjectIdNotEqual(BaseMongoEngineFilter):
    def apply(self, query, value):
        column_name = self.column.name
        flt = {'%s__ne' % column_name: value}
        return query.filter(**flt)

    def operation(self):
        return gettext('ObjectId not equal')

class FilterObjectIdIn(BaseMongoEngineFilter):
    def apply(self, query, value):
        column_name = self.column.name
        value = [v.strip() for v in value.split(',')]
        flt = {'%s__in' % column_name: value}
        return query.filter(**flt)

    def operation(self):
        return gettext('ObjectId in')

class FilterObjectIdNotIn(BaseMongoEngineFilter):
    def apply(self, query, value):
        column_name = self.column.name
        value = [v.strip() for v in value.split(',')]
        flt = {'%s__nin' % column_name: value}
        return query.filter(**flt)

    def operation(self):
        return gettext('ObjectId not in')


# Base MongoEngine filter field converter
class FilterConverter(filters.BaseFilterConverter):
    strings = (FilterEqual, FilterNotEqual, FilterLike, FilterNotLike)
    numeric = (FilterEqual, FilterNotEqual, FilterGreater, FilterSmaller)
    objectid = (FilterObjectIdEqual, FilterObjectIdNotEqual,
               FilterObjectIdIn, FilterObjectIdNotIn)
    lists = (FilterEqual, FilterNotEqual)

    def convert(self, type_name, column, name):
        if type_name in self.converters:
            return self.converters[type_name](column, name)

        return None

    @filters.convert('StringField', 'EmailField')
    def conv_string(self, column, name):
        return [f(column, name) for f in self.strings]

    @filters.convert('BooleanField')
    def conv_bool(self, column, name):
        return [BooleanEqualFilter(column, name),
                BooleanNotEqualFilter(column, name)]

    @filters.convert('IntField', 'DecimalField', 'FloatField')
    def conv_int(self, column, name):
        return [f(column, name) for f in self.numeric]

    @filters.convert('DateField')
    def conv_date(self, column, name):
        return [f(column, name, data_type='datepicker') for f in self.numeric]

    @filters.convert('DateTimeField')
    def conv_datetime(self, column, name):
        return [f(column, name, data_type='datetimepicker')
                for f in self.numeric]
    
    @filters.convert('ObjectIdField')
    def conv_objectid(self, column, name):
        return [f(column, name) for f in self.objectid]

    @filters.convert('ListField')
    def conv_list(self, column, name):
        return [f(column, name) for f in self.lists]
    
