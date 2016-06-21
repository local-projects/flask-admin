import datetime

from flask_admin.babel import lazy_gettext
from flask_admin.model import filters

from .tools import parse_like_term
from mongoengine.queryset import Q
from bson.errors import InvalidId
from bson.objectid import ObjectId


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
        return lazy_gettext('equals')


class FilterNotEqual(BaseMongoEngineFilter):
    def apply(self, query, value):
        flt = {'%s__ne' % self.column.name: value}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('not equal')


class FilterLike(BaseMongoEngineFilter):
    def apply(self, query, value):
        term, data = parse_like_term(value)
        flt = {'%s__%s' % (self.column.name, term): data}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('contains')


class FilterNotLike(BaseMongoEngineFilter):
    def apply(self, query, value):
        term, data = parse_like_term(value)
        flt = {'%s__not__%s' % (self.column.name, term): data}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('not contains')


class FilterGreater(BaseMongoEngineFilter):
    def apply(self, query, value):
        flt = {'%s__gt' % self.column.name: value}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('greater than')


class FilterSmaller(BaseMongoEngineFilter):
    def apply(self, query, value):
        flt = {'%s__lt' % self.column.name: value}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('smaller than')


class FilterEmpty(BaseMongoEngineFilter, filters.BaseBooleanFilter):
    def apply(self, query, value):
        if value == '1':
            flt = {'%s' % self.column.name: None}
        else:
            flt = {'%s__ne' % self.column.name: None}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('empty')


class FilterInList(BaseMongoEngineFilter):
    def __init__(self, column, name, options=None, data_type=None):
        super(FilterInList, self).__init__(column, name, options, data_type='select2-tags')

    def clean(self, value):
        return [v.strip() for v in value.split(',') if v.strip()]

    def apply(self, query, value):
        flt = {'%s__in' % self.column.name: value}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('in list')


class FilterNotInList(FilterInList):
    def apply(self, query, value):
        flt = {'%s__nin' % self.column.name: value}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('not in list')


# Customized type filters
class BooleanEqualFilter(FilterEqual, filters.BaseBooleanFilter):
    def apply(self, query, value):
        flt = {'%s' % self.column.name: value == '1'}
        return query.filter(**flt)


class BooleanNotEqualFilter(FilterNotEqual, filters.BaseBooleanFilter):
    def apply(self, query, value):
        flt = {'%s' % self.column.name: value != '1'}
        return query.filter(**flt)


class IntEqualFilter(FilterEqual, filters.BaseIntFilter):
    pass


class IntNotEqualFilter(FilterNotEqual, filters.BaseIntFilter):
    pass


class IntGreaterFilter(FilterGreater, filters.BaseIntFilter):
    pass


class IntSmallerFilter(FilterSmaller, filters.BaseIntFilter):
    pass


class IntInListFilter(filters.BaseIntListFilter, FilterInList):
    pass


class IntNotInListFilter(filters.BaseIntListFilter, FilterNotInList):
    pass


class FloatEqualFilter(FilterEqual, filters.BaseFloatFilter):
    pass


class FloatNotEqualFilter(FilterNotEqual, filters.BaseFloatFilter):
    pass


class FloatGreaterFilter(FilterGreater, filters.BaseFloatFilter):
    pass


class FloatSmallerFilter(FilterSmaller, filters.BaseFloatFilter):
    pass


class FloatInListFilter(filters.BaseFloatListFilter, FilterInList):
    pass


class FloatNotInListFilter(filters.BaseFloatListFilter, FilterNotInList):
    pass


class DateTimeEqualFilter(FilterEqual, filters.BaseDateTimeFilter):
    pass


class DateTimeNotEqualFilter(FilterNotEqual, filters.BaseDateTimeFilter):
    pass


class DateTimeGreaterFilter(FilterGreater, filters.BaseDateTimeFilter):
    pass


class DateTimeSmallerFilter(FilterSmaller, filters.BaseDateTimeFilter):
    pass


class DateTimeBetweenFilter(BaseMongoEngineFilter, filters.BaseDateTimeBetweenFilter):
    def __init__(self, column, name, options=None, data_type=None):
        super(DateTimeBetweenFilter, self).__init__(column,
                                                    name,
                                                    options,
                                                    data_type='datetimerangepicker')

    def apply(self, query, value):
        start, end = value
        flt = {'%s__gte' % self.column.name: start, '%s__lte' % self.column.name: end}
        return query.filter(**flt)


class DateTimeNotBetweenFilter(DateTimeBetweenFilter):
    def apply(self, query, value):
        start, end = value
        return query.filter(Q(**{'%s__not__gte' % self.column.name: start}) |
                            Q(**{'%s__not__lte' % self.column.name: end}))

    def operation(self):
        return lazy_gettext('not between')


class ReferenceObjectIdFilter(BaseMongoEngineFilter):
    def validate(self, value):
        """
            Validate value.
            If value is valid, returns `True` and `False` otherwise.
            :param value:
                Value to validate
        """
        try:
            self.clean(value)
            return True
        except InvalidId:
            return False

    def clean(self, value):
        return ObjectId(value.strip())

    def apply(self, query, value):
        flt = {'%s' % self.column.name: value}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('ObjectId equals')


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

 
class OIdsMatchFilter(BaseMongoEngineFilter):
    def apply(self, query, value):
        flt = {self.column.name: ObjectId(value)}
        return query.filter(**flt)

    def operation(self):
        return gettext('with id')
   
    # You can validate values. If value is not valid,
    # return `False`, so filter will be ignored.
    def validate(self, value):
        return ObjectId.is_valid(value)

    # You can "clean" values before they will be
    # passed to the your data access layer
    def clean(self, value):
        return value

class ExistenceFilter(BaseMongoEngineFilter):
    def apply(self, query, value):
        flt = { "%s__0__exists" % self.column.name: is_true(value) }
        return query.filter(**flt)

    def validate(self, value):
        # Basically all values are valid since the is_true() function will process it
        return True

    def operation(self):
        return gettext('exists')
   
    # You can "clean" values before they will be
    # passed to the your data access layer
    def clean(self, value):
        return is_true(value)
    
class EmbeddedDocumentFieldFilter(BaseMongoEngineFilter):
    """Return matches based on an embeddedDocument's string fields"""
    def apply(self, query, value):
        qfilt = None
        if isinstance(self.column, EmbeddedDocumentField):
            # Extract out all the string fields for comparison
            for fieldname, fieldtype in self.column.document_type._fields.items():
                if isinstance(fieldtype, (StringField)):
                    if not qfilt:
                        # qfilt = Q(applications__slug=value)
                        qfilt = Q(**{"%s__%s" % (self.column.name, fieldname): value})
                    else:
                        qfilt = qfilt._combine(other=Q(**{"%s__%s" % (self.column.name, fieldname): value}), 
                                               operation=Q.OR)
            
        return query.filter(qfilt)

    def operation(self):
        return gettext("contains")

    def clean(self, value):
        return value

#     def validate(self, value):
#         if not isinstance(self.column, EmbeddedDocumentField):
#             raise Exception("Programming Error: Column %s is not an EmbeddedDocumentField." % str(self.column))


class ReferenceFieldFilter(BaseMongoEngineFilter):
    """Return matches based on a referenced field"""
    def apply(self, query, value):
        # If this is a referencefield, we may have to extract the specific referenced-field
        flt = {self.column.name: value}
        return query.filter(**flt)
    
    def operation(self):
        return gettext("equals")
    
    def clean(self, value):
        return value

    # You can validate values. If value is not valid,
    # return `False`, so filter will be ignored.
    def validate(self, value):
        return ObjectId.is_valid(value)


# Base MongoEngine filter field converter
class FilterConverter(filters.BaseFilterConverter):
    strings = (FilterLike, FilterNotLike, FilterEqual, FilterNotEqual,
               FilterEmpty, FilterInList, FilterNotInList)
    int_filters = (IntEqualFilter, IntNotEqualFilter, IntGreaterFilter,
                   IntSmallerFilter, FilterEmpty, IntInListFilter,
                   IntNotInListFilter)
    float_filters = (FloatEqualFilter, FloatNotEqualFilter, FloatGreaterFilter,
                     FloatSmallerFilter, FilterEmpty, FloatInListFilter,
                     FloatNotInListFilter)
    bool_filters = (BooleanEqualFilter, BooleanNotEqualFilter)
    datetime_filters = (DateTimeEqualFilter, DateTimeNotEqualFilter,
                        DateTimeGreaterFilter, DateTimeSmallerFilter,
                        DateTimeBetweenFilter, DateTimeNotBetweenFilter,
                        FilterEmpty)
    reference_filters = (ReferenceObjectIdFilter,)

    objectid_filters = (FilterObjectIdEqual, FilterObjectIdNotEqual,
               FilterObjectIdIn, FilterObjectIdNotIn)
    lists_filters = (FilterEqual, FilterNotEqual)

    def convert(self, type_name, column, name):
        filter_name = type_name.lower()

        if filter_name in self.converters:
            return self.converters[filter_name](column, name)

        return None


    @filters.convert('StringField', 'EmailField', 'URLField')
    def conv_string(self, column, name):
        return [f(column, name) for f in self.strings]

    @filters.convert('BooleanField')
    def conv_bool(self, column, name):
        return [f(column, name) for f in self.bool_filters]

    @filters.convert('IntField', 'LongField')
    def conv_int(self, column, name):
        return [f(column, name) for f in self.int_filters]

    @filters.convert('DecimalField', 'FloatField')
    def conv_float(self, column, name):
        return [f(column, name) for f in self.float_filters]

    @filters.convert('DateTimeField', 'ComplexDateTimeField')
    def conv_datetime(self, column, name):
        return [f(column, name) for f in self.datetime_filters]

    @filters.convert('ReferenceField')
    def conv_reference(self, column, name):
        return [f(column, name) for f in self.reference_filters]

    @filters.convert('ObjectIdField')
    def conv_objectid(self, column, name):
        return [f(column, name) for f in self.objectid_filters]

    @filters.convert('ListField')
    def conv_list(self, column, name):
        return [f(column, name) for f in self.lists_filters]
