from nose.tools import eq_, ok_
from nose.plugins.skip import SkipTest

# Skip test on PY3
from flask.ext.admin._compat import PY2, as_unicode
if not PY2:
    raise SkipTest('MongoEngine is not Python 3 compatible')

from wtforms import fields
from flask.ext.admin.model import fields as fafields
from flask.ext.admin import form, expose
from flask.ext.admin.contrib.mongoengine import ModelView
from flask_admin.contrib.mongoengine.fields import ModelFormField
from flask_mongoengine.wtf.fields import DictField, ModelSelectMultipleField

from . import setup


class CustomModelView(ModelView):
    def __init__(self, model,
                 name=None, category=None, 
                 endpoint=None, url=None,
                 **kwargs):

        for k, v in kwargs.iteritems():
            setattr(self, k, v)

        super(CustomModelView, self).__init__(model,
                                              name, category,
                                              endpoint, url)


class BookModelView(CustomModelView):
    def create_form(self):
        form = super(BookModelView, self).create_form()
        return form

    def edit_form(self, obj):
        form = super(BookModelView, self).edit_form(obj)
        return form



def create_models(db):
    class Author(db.EmbeddedDocument):
        name = db.StringField(max_length=20)
        email = db.StringField(max_length=20)

    class Publisher(db.Document):
        refid = db.IntField()
        active = db.BooleanField()

    class Book(db.Document):
        title = db.StringField(max_length=20)
        tags = db.ListField(db.StringField())
        publishers = db.ListField(db.ReferenceField('Publisher'))
        authors = db.ListField(db.EmbeddedDocumentField(Author))
        info = db.DictField()

    Book.objects.delete()
    Publisher.objects.delete()

    return Book, Publisher, Author


def test_model():
    app, db, admin = setup()

    Book, Publisher, Author = create_models(db)

    view = BookModelView(Book)

    admin.add_view(view)

    eq_(view.model, Book)
    eq_(view.name, 'Book')
    eq_(view.endpoint, 'bookview')

    eq_(view._primary_key, 'id')

    # None of the complex fields can be sorted on
    ok_('title' in view._sortable_columns)

    # Verify form
    eq_(view._create_form_class.title.field_class, fields.StringField)
    eq_(view._create_form_class.tags.field_class, fafields.InlineFieldList)
    eq_(view._create_form_class.authors.field_class, fafields.InlineFieldList)
    eq_(view._create_form_class.publishers.field_class, ModelSelectMultipleField)
    eq_(view._create_form_class.info.field_class, DictField)

    publisher = Publisher(refid=1, 
                          active=True)
    publisher.save()
    author = Author(name='name', 
                    email='a@b.com')

    # Make some test clients
    with app.test_client() as client:
        rv = client.get('/admin/bookview/')
        eq_(rv.status_code, 200)

        rv = client.get('/admin/bookview/new/')
        eq_(rv.status_code, 200)

        rv = client.post('/admin/bookview/new/',
                         data=dict(title= 'test',
                                   tags= ["a,b,c"],
                                   publishers= [str(publisher.id)],
                                   authors= [author]
                              ))
        eq_(rv.status_code, 302)

        from nose.tools import set_trace; set_trace()
        book = Book.objects.first()
        ok_(book.title == 'test')

        ok_(book.tags == ['a','b','c'])
        ok_(book.publishers[0].id == publisher.id)
        ok_(book.authors[0].name == 'name')
        ok_(book.authors[0].email == 'a@b.com')

        # Update the list of tags
        rv = client.post('/admin/bookview/edit/?id=%s' % book.id,
                         data={'tags': ['c','b','a']})
        eq_(rv.status_code, 200)
        edbook = Book.objects().with_id(book.id)
        ok_(book.tags == ['c','b','a'])


def test_subdocument_config():
    app, db, admin = setup()

    class Comment(db.EmbeddedDocument):
        name = db.StringField(max_length=20, required=True)
        value = db.StringField(max_length=20)

    class Model1(db.Document):
        test1 = db.StringField(max_length=20)
        subdoc = db.EmbeddedDocumentField(Comment)

    # Check only
    view1 = CustomModelView(
        Model1,
        form_subdocuments = {
            'subdoc': {
                'form_columns': ('name',)
            }
        }
    )

    ok_(hasattr(view1._create_form_class, 'subdoc'))

    form = view1.create_form()
    ok_('name' in dir(form.subdoc.form))
    ok_('value' not in dir(form.subdoc.form))

    # Check exclude
    view2 = CustomModelView(
        Model1,
        form_subdocuments = {
            'subdoc': {
                'form_excluded_columns': ('value',)
            }
        }
    )

    form = view2.create_form()
    ok_('name' in dir(form.subdoc.form))
    ok_('value' not in dir(form.subdoc.form))


def test_subdocument_class_config():
    app, db, admin = setup()

    from flask.ext.admin.contrib.mongoengine import EmbeddedForm

    class Comment(db.EmbeddedDocument):
        name = db.StringField(max_length=20, required=True)
        value = db.StringField(max_length=20)

    class Model1(db.Document):
        test1 = db.StringField(max_length=20)
        subdoc = db.EmbeddedDocumentField(Comment)

    class EmbeddedConfig(EmbeddedForm):
        form_columns = ('name',)

    # Check only
    view1 = CustomModelView(
        Model1,
        form_subdocuments = {
            'subdoc': EmbeddedConfig()
        }
    )

    form = view1.create_form()
    ok_('name' in dir(form.subdoc.form))
    ok_('value' not in dir(form.subdoc.form))


def test_nested_subdocument_config():
    app, db, admin = setup()

    # Check recursive
    class Comment(db.EmbeddedDocument):
        name = db.StringField(max_length=20, required=True)
        value = db.StringField(max_length=20)

    class Nested(db.EmbeddedDocument):
        name = db.StringField(max_length=20, required=True)
        comment = db.EmbeddedDocumentField(Comment)

    class Model1(db.Document):
        test1 = db.StringField(max_length=20)
        nested = db.EmbeddedDocumentField(Nested)

    view1 = CustomModelView(
        Model1,
        form_subdocuments = {
            'nested': {
                'form_subdocuments': {
                    'comment': {
                        'form_columns': ('name',)
                    }
                }
            }
        }
    )

    form = view1.create_form()
    ok_('name' in dir(form.nested.form.comment.form))
    ok_('value' not in dir(form.nested.form.comment.form))


def test_nested_list_subdocument():
    app, db, admin = setup()

    class Comment(db.EmbeddedDocument):
        name = db.StringField(max_length=20, required=True)
        value = db.StringField(max_length=20)

    class Model1(db.Document):
        test1 = db.StringField(max_length=20)
        subdoc = db.ListField(db.EmbeddedDocumentField(Comment))

    # Check only
    view1 = CustomModelView(
        Model1,
        form_subdocuments = {
            'subdoc': {
                'form_subdocuments': {
                    None: {
                        'form_columns': ('name',)
                    }
                }

            }
        }
    )

    form = view1.create_form()
    inline_form = form.subdoc.unbound_field.args[2]

    ok_('name' in dir(inline_form))
    ok_('value' not in dir(inline_form))


def test_ajax_fk():
    app, db, admin = setup()

    class Model1(db.Document):
        test1 = db.StringField(max_length=20)
        test2 = db.StringField(max_length=20)

        def __str__(self):
            return self.test1

    class Model2(db.Document):
        int_field = db.IntField()
        bool_field = db.BooleanField()

        model1 = db.ReferenceField(Model1)

    Model1.objects.delete()
    Model2.objects.delete()

    view = CustomModelView(
        Model2,
        url='view',
        form_ajax_refs={
            'model1': {
                'fields': ('test1', 'test2')
            }
        }
    )
    admin.add_view(view)

    ok_(u'model1' in view._form_ajax_refs)

    model = Model1(test1=u'first')
    model.save()
    model2 = Model1(test1=u'foo', test2=u'bar').save()

    # Check loader
    loader = view._form_ajax_refs[u'model1']
    mdl = loader.get_one(model.id)
    eq_(mdl.test1, model.test1)

    items = loader.get_list(u'fir')
    eq_(len(items), 1)
    eq_(items[0].id, model.id)

    items = loader.get_list(u'bar')
    eq_(len(items), 1)
    eq_(items[0].test1, u'foo')

    # Check form generation
    form = view.create_form()
    eq_(form.model1.__class__.__name__, u'AjaxSelectField')

    with app.test_request_context('/admin/view/'):
        ok_(u'value=""' not in form.model1())

        form.model1.data = model
        needle = u'data-json="[&quot;%s&quot;, &quot;first&quot;]"' % as_unicode(model.id)
        ok_(needle in form.model1())
        ok_(u'value="%s"' % as_unicode(model.id) in form.model1())

    # Check querying
    client = app.test_client()

    req = client.get(u'/admin/view/ajax/lookup/?name=model1&query=foo')
    eq_(req.data, u'[["%s", "foo"]]' % model2.id)

    # Check submitting
    client.post('/admin/view/new/', data={u'model1': as_unicode(model.id)})
    mdl = Model2.objects.first()

    ok_(mdl is not None)
    ok_(mdl.model1 is not None)
    eq_(mdl.model1.id, model.id)
    eq_(mdl.model1.test1, u'first')


def test_nested_ajax_refs():
    app, db, admin = setup()

    # Check recursive
    class Comment(db.Document):
        name = db.StringField(max_length=20, required=True)
        value = db.StringField(max_length=20)

    class Nested(db.EmbeddedDocument):
        name = db.StringField(max_length=20, required=True)
        comment = db.ReferenceField(Comment)

    class Model1(db.Document):
        test1 = db.StringField(max_length=20)
        nested = db.EmbeddedDocumentField(Nested)

    view1 = CustomModelView(
        Model1,
        form_subdocuments = {
            'nested': {
                'form_ajax_refs': {
                    'comment': {
                        'fields': ['name']
                    }
                }
            }
        }
    )

    form = view1.create_form()
    eq_(type(form.nested.form.comment).__name__, 'AjaxSelectField')
    ok_('nested-comment' in view1._form_ajax_refs)


def test_form_flat_choices():
    app, db, admin = setup()

    class Model(db.Document):
        name = db.StringField(max_length=20, choices=('a', 'b', 'c'))

    view = CustomModelView(Model)
    admin.add_view(view)

    form = view.create_form()
    eq_(form.name.choices, [('a', 'a'), ('b', 'b'), ('c', 'c')])


def test_form_args_embeddeddoc():
    app, db, admin = setup()

    class Info(db.EmbeddedDocument):
        name = db.StringField()
        age = db.StringField()

    class Model(db.Document):
        info = db.EmbeddedDocumentField('Info')
        timestamp = db.DateTimeField()

    view = CustomModelView(
        Model,
        form_args= {
            'info': {'label': 'Information'},
            'timestamp': {'label': 'Last Updated Time'}
        }
    )
    admin.add_view(view)
    form = view.create_form()
    eq_(form.timestamp.label.text, 'Last Updated Time')
    # This is the failure
    eq_(form.info.label.text, 'Information')
