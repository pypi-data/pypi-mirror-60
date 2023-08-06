from enum import (
    Enum,
    auto,
)
from functools import total_ordering
from itertools import groupby
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Type,
    Union,
)

from django.conf import settings
from django.core.paginator import (
    InvalidPage,
    Paginator as DjangoPaginator,
)
from django.db.models import QuerySet
from django.http import (
    Http404,
    HttpResponseRedirect,
)
from django.utils.encoding import (
    force_str,
)
from django.utils.html import (
    conditional_escape,
    format_html,
)
from django.utils.safestring import mark_safe
from iommi._web_compat import (
    Template,
    render_template,
)
from iommi.action import (
    Action,
    group_actions,
)
from iommi.base import (
    DISPATCH_PREFIX,
    MISSING,
    PagePart,
    bind_members,
    collect_members,
    evaluate_attrs,
    evaluate_member,
    evaluate_members,
    evaluate_strict_container,
    model_and_rows,
    no_copy_on_bind,
    path_join,
    setup_endpoint_proxies,
)
from iommi.form import (
    Form,
)
from iommi.from_model import (
    create_members_from_model,
    member_from_model,
)
from iommi.query import (
    Q_OP_BY_OP,
    Query,
    QueryException,
)
from tri_declarative import (
    EMPTY,
    LAST,
    Namespace,
    Refinable,
    RefinableObject,
    class_shortcut,
    declarative,
    dispatch,
    evaluate,
    evaluate_strict,
    getattr_path,
    refinable,
    setattr_path,
    setdefaults_path,
    with_meta,
)
from tri_struct import (
    Struct,
)

LAST = LAST

_column_factory_by_field_type = {}


def register_column_factory(field_class, factory):
    _column_factory_by_field_type[field_class] = factory


DESCENDING = 'descending'
ASCENDING = 'ascending'

DEFAULT_PAGE_SIZE = 40


def prepare_headers(table, columns):
    request = table.request()
    if request is None:
        return

    for column in columns:
        if column.sortable:
            params = request.GET.copy()
            param_path = path_join(table.path(), 'order')
            order = request.GET.get(param_path, None)
            start_sort_desc = column.sort_default_desc
            params[param_path] = column.name if not start_sort_desc else '-' + column.name
            column.is_sorting = False
            if order is not None:
                is_desc = order.startswith('-')
                order_field = order if not is_desc else order[1:]
                if order_field == column.name:
                    new_order = order_field if is_desc else ('-' + order_field)
                    params[param_path] = new_order
                    column.sort_direction = DESCENDING if is_desc else ASCENDING
                    column.is_sorting = True

            column.url = "?" + params.urlencode()
        else:
            column.is_sorting = False


@total_ordering
class MinType(object):
    def __le__(self, other):
        return True

    def __eq__(self, other):
        return self is other


MIN = MinType()


def order_by_on_list(objects, order_field, is_desc=False):
    """
    Utility function to sort objects django-style even for non-query set collections

    :param objects: list of objects to sort
    :param order_field: field name, follows django conventions, so `foo__bar` means `foo.bar`, can be a callable.
    :param is_desc: reverse the sorting
    :return:
    """
    if callable(order_field):
        objects.sort(key=order_field, reverse=is_desc)
        return

    def order_key(x):
        v = getattr_path(x, order_field)
        if v is None:
            return MIN
        return v

    objects.sort(key=order_key, reverse=is_desc)


def yes_no_formatter(value, **_):
    """ Handle True/False from Django model and 1/0 from raw sql """
    if value is None:
        return ''
    if value == 1:  # boolean True is equal to 1
        return 'Yes'
    if value == 0:  # boolean False is equal to 0
        return 'No'
    assert False, f"Unable to convert {value} to Yes/No"


def list_formatter(value, **_):
    return ', '.join([conditional_escape(x) for x in value])


_cell_formatters = {
    bool: yes_no_formatter,
    tuple: list_formatter,
    list: list_formatter,
    set: list_formatter,
    QuerySet: lambda value, **_: list_formatter(list(value))
}


def register_cell_formatter(type_or_class, formatter):
    """
    Register a default formatter for a type. A formatter is a function that takes four keyword arguments: table, column, row, value
    """
    global _cell_formatters
    _cell_formatters[type_or_class] = formatter


def default_cell_formatter(table: 'Table', column: 'Column', row, value, **_):
    formatter = _cell_formatters.get(type(value))
    if formatter:
        value = formatter(table=table, column=column, row=row, value=value)

    if value is None:
        return ''

    return conditional_escape(value)


SELECT_DISPLAY_NAME = '<i class="fa fa-check-square-o" onclick="iommi_table_js_select_all(this)"></i>'


class DataRetrievalMethods(Enum):
    attribute_access = auto()
    prefetch = auto()
    select = auto()


@with_meta
class Column(PagePart):
    """
    Class that describes a column, i.e. the text of the header, how to get and display the data in the cell, etc.
    """
    url: str = Refinable()
    attr: str = Refinable()
    sort_default_desc: bool = Refinable()
    sortable: bool = Refinable()
    group: Optional[str] = Refinable()
    auto_rowspan: bool = Refinable()
    cell: Namespace = Refinable()
    model = Refinable()
    model_field = Refinable()
    choices: Iterable = Refinable()
    bulk: Namespace = Refinable()
    query: Namespace = Refinable()
    superheader = Refinable()
    header: Namespace = Refinable()
    data_retrieval_method = Refinable()
    render_column: bool = Refinable()

    @dispatch(
        attr=MISSING,
        sort_default_desc=False,
        sortable=True,
        auto_rowspan=False,
        bulk__include=False,
        query__include=False,
        query__form__include=False,
        data_retrieval_method=DataRetrievalMethods.attribute_access,
        cell__template=None,
        cell__attrs=EMPTY,
        cell__value=lambda column, row, **kwargs: getattr_path(row, evaluate_strict(column.attr, row=row, column=column, **kwargs)),
        cell__format=default_cell_formatter,
        cell__url=None,
        cell__url_title=None,
        header__attrs__class__sorted_column=lambda column, **_: column.is_sorting,
        header__attrs__class__descending=lambda column, **_: column.sort_direction == DESCENDING,
        header__attrs__class__ascending=lambda column, **_: column.sort_direction == ASCENDING,
        header__attrs__class__first_column=lambda header, **_: header.index_in_group == 0,
        header__attrs__class__subheader=True,
        header__template='iommi/table/header.html',
        render_column=True,
        default_child=False,
    )
    def __init__(self, **kwargs):
        """
        :param name: the name of the column
        :param attr: What attribute to use, defaults to same as name. Follows django conventions to access properties of properties, so `foo__bar` is equivalent to the python code `foo.bar`. This parameter is based on the variable name of the Column if you use the declarative style of creating tables.
        :param display_name: the text of the header for this column. By default this is based on the `name` parameter so normally you won't need to specify it.
        :param url: URL of the header. This should only be used if "sorting" is off.
        :param include: set this to `False` to hide the column
        :param sortable: set this to `False` to disable sorting on this column
        :param sort_key: string denoting what value to use as sort key when this column is selected for sorting. (Or callable when rendering a table from list.)
        :param sort_default_desc: Set to `True` to make table sort link to sort descending first.
        :param group: string describing the group of the header. If this parameter is used the header of the table now has two rows. Consecutive identical groups on the first level of the header are joined in a nice way.
        :param auto_rowspan: enable automatic rowspan for this column. To join two cells with rowspan, just set this auto_rowspan to True and make those two cells output the same text and we'll handle the rest.
        :param cell__template: name of a template file, or `Template` instance. Gets arguments: `table`, `column`, `bound_row`, `row` and `value`. Your own arguments should be sent in the 'extra' parameter.
        :param cell__value: string or callable that receives kw arguments: `table`, `column` and `row`. This is used to extract which data to display from the object.
        :param cell__format: string or callable that receives kw arguments: `table`, `column`, `row` and `value`. This is used to convert the extracted data to html output (use `mark_safe`) or a string.
        :param cell__attrs: dict of attr name to callables that receive kw arguments: `table`, `column`, `row` and `value`.
        :param cell__url: callable that receives kw arguments: `table`, `column`, `row` and `value`.
        :param cell__url_title: callable that receives kw arguments: `table`, `column`, `row` and `value`.
        :param render_column: If set to `False` the column won't be rendered in the table, but still be available in `table.columns`. This can be useful if you want some other feature from a column like filtering.
        """

        super(Column, self).__init__(**kwargs)

        # TODO: this seems weird.. why do we need this?
        self.declared_column: Column = None
        self.is_sorting: bool = None
        self.sort_direction: str = None

    def __repr__(self):
        return '<{}.{} {}>'.format(self.__class__.__module__, self.__class__.__name__, self.name)

    @property
    def table(self):
        return self.parent

    @staticmethod
    @refinable
    def sort_key(table, column, **_):
        return column.attr

    @staticmethod
    @refinable
    def display_name(table, column, **_):
        return force_str(column.name).rsplit('__', 1)[-1].replace("_", " ").capitalize()

    def on_bind(self) -> None:
        for k, v in getattr(self.parent.parent, '_columns_unapplied_data').get(self.name, {}).items():
            setattr_path(self, k, v)

        if self.attr is MISSING:
            self.attr = self.name

        self.header.attrs = Namespace(self.header.attrs.copy())
        self.header.attrs['class'] = Namespace(self.header.attrs['class'].copy())

        self.bulk = setdefaults_path(
            Struct(),
            self.bulk,
            attr=self.attr,
        )
        self.query = setdefaults_path(
            Struct(),
            self.query,
            attr=self.attr,
        )
        self.declared_column = self._declared

        # Not strict evaluate on purpose
        self.model = evaluate(self.model, **self.evaluate_attribute_kwargs())

        evaluated_attributes = [
            'name',
            'include',
            'attr',
            'after',
            'default_child',
            'style',
            'url',
            'sort_default_desc',
            'sortable',
            'group',
            'auto_rowspan',
            'choices',
            'superheader',
            'header',
            'data_retrieval_method',
            'render_column',
            'attr',
            'sort_key',
            'display_name',
            # TODO: not sure about these
            # 'model_field',
            # 'cell',
            # 'bulk',
            # 'query',
            # 'extra',
        ]
        evaluate_members(self, evaluated_attributes, **self.evaluate_attribute_kwargs())
        self.extra_evaluated = evaluate_strict_container(self.extra_evaluated, **self.evaluate_attribute_kwargs())

    def _evaluate_attribute_kwargs(self):
        return dict(table=self.parent, column=self)

    @classmethod
    @dispatch(
        query__call_target__attribute='from_model',
        bulk__call_target__attribute='from_model',
    )
    def from_model(cls, model, field_name=None, model_field=None, **kwargs):
        return member_from_model(
            cls=cls,
            model=model,
            factory_lookup=_column_factory_by_field_type,
            factory_lookup_register_function=register_column_factory,
            field_name=field_name,
            model_field=model_field,
            defaults_factory=lambda model_field: {},
            **kwargs)

    @classmethod
    @class_shortcut(
        display_name='',
        sortable=False,
        header__attrs__class__thin=True,
        cell__value=lambda table, **_: True,
        cell__attrs__class__cj=True,
    )
    def icon(cls, icon, icon_title=None, include=True, call_target=None, **kwargs):
        """
        Shortcut to create font awesome-style icons.

        :param icon: the font awesome name of the icon
        """
        setdefaults_path(kwargs, dict(
            include=lambda table, **rest: evaluate_strict(include, table=table, **rest),
            header__attrs__title=icon_title,
            cell__format=lambda value, **_: mark_safe('<i class="fa fa-lg fa-%s"%s></i>' % (icon, ' title="%s"' % icon_title if icon_title else '')) if value else ''
        ))
        return call_target(**kwargs)

    @classmethod
    @class_shortcut(
        call_target__attribute='icon',
        cell__url=lambda row, **_: row.get_absolute_url() + 'edit/',
        display_name=''
    )
    def edit(cls, call_target=None, **kwargs):
        """
        Shortcut for creating a clickable edit icon. The URL defaults to `your_object.get_absolute_url() + 'edit/'`. Specify the option cell__url to override.
        """
        return call_target('pencil-square-o', 'Edit', **kwargs)

    @classmethod
    @class_shortcut(
        call_target__attribute='icon',
        cell__url=lambda row, **_: row.get_absolute_url() + 'delete/',
        display_name=''
    )
    def delete(cls, call_target=None, **kwargs):
        """
        Shortcut for creating a clickable delete icon. The URL defaults to `your_object.get_absolute_url() + 'delete/'`. Specify the option cell__url to override.
        """
        return call_target('trash-o', 'Delete', **kwargs)

    @classmethod
    @class_shortcut(
        call_target__attribute='icon',
        cell__url=lambda row, **_: row.get_absolute_url() + 'download/',
        cell__value=lambda row, **_: getattr(row, 'pk', False),
    )
    def download(cls, call_target=None, **kwargs):
        """
        Shortcut for creating a clickable download icon. The URL defaults to `your_object.get_absolute_url() + 'download/'`. Specify the option cell__url to override.
        """
        return call_target('download', 'Download', **kwargs)

    @classmethod
    @class_shortcut(
        header__attrs__title='Run',
        sortable=False,
        header__attrs__class__thin=True,
        cell__url=lambda row, **_: row.get_absolute_url() + 'run/',
        cell__value='Run',
    )
    def run(cls, include=True, call_target=None, **kwargs):
        """
        Shortcut for creating a clickable run icon. The URL defaults to `your_object.get_absolute_url() + 'run/'`. Specify the option cell__url to override.
        """
        setdefaults_path(kwargs, dict(
            include=lambda table, **rest: evaluate_strict(include, table=table, **rest),
        ))
        return call_target(**kwargs)

    @classmethod
    @class_shortcut(
        display_name=mark_safe(SELECT_DISPLAY_NAME),
        sortable=False,
    )
    def select(cls, checkbox_name='pk', include=True, checked=lambda x: False, call_target=None, **kwargs):
        """
        Shortcut for a column of checkboxes to select rows. This is useful for implementing bulk operations.

        :param checkbox_name: the name of the checkbox. Default is `"pk"`, resulting in checkboxes like `"pk_1234"`.
        :param checked: callable to specify if the checkbox should be checked initially. Defaults to `False`.
        """
        setdefaults_path(kwargs, dict(
            include=lambda table, **rest: evaluate_strict(include, table=table, **rest),
            cell__value=lambda row, **_: mark_safe('<input type="checkbox"%s class="checkbox" name="%s_%s" />' % (' checked' if checked(row.pk) else '', checkbox_name, row.pk)),
        ))
        return call_target(**kwargs)

    @classmethod
    @class_shortcut(
        cell__attrs__class__cj=True,
        query__call_target__attribute='boolean',
        bulk__call_target__attribute='boolean',
    )
    def boolean(cls, call_target=None, **kwargs):
        """
        Shortcut to render booleans as a check mark if true or blank if false.
        """

        def render_icon(value):
            if callable(value):
                value = value()
            return mark_safe('<i class="fa fa-check" title="Yes"></i>') if value else ''

        setdefaults_path(kwargs, dict(
            cell__format=lambda value, **rest: render_icon(value),
        ))
        return call_target(**kwargs)

    @classmethod
    @class_shortcut(
        call_target__attribute='boolean',
        query__call_target__attribute='boolean_tristate',
    )
    def boolean_tristate(cls, *args, **kwargs):
        call_target = kwargs.pop('call_target', cls)
        return call_target(*args, **kwargs)

    @classmethod
    @class_shortcut(
        bulk__call_target__attribute='choice',
        query__call_target__attribute='choice',
    )
    def choice(cls, call_target=None, **kwargs):
        choices = kwargs['choices']
        setdefaults_path(kwargs, dict(
            bulk__choices=choices,
            query__choices=choices,
        ))
        return call_target(**kwargs)

    @classmethod
    @class_shortcut(
        call_target__attribute='choice',
        bulk__call_target__attribute='choice_queryset',
        query__call_target__attribute='choice_queryset',
    )
    def choice_queryset(cls, call_target=None, **kwargs):
        setdefaults_path(kwargs, dict(
            bulk__model=kwargs.get('model'),
            query__model=kwargs.get('model'),
        ))
        return call_target(**kwargs)

    @classmethod
    @class_shortcut(
        call_target__attribute='choice_queryset',
        bulk__call_target__attribute='multi_choice_queryset',
        query__call_target__attribute='multi_choice_queryset',
    )
    def multi_choice_queryset(cls, call_target, **kwargs):
        setdefaults_path(kwargs, dict(
            bulk__model=kwargs.get('model'),
            query__model=kwargs.get('model'),
        ))
        return call_target(**kwargs)

    @classmethod
    @class_shortcut(
        call_target__attribute='choice',
        bulk__call_target__attribute='multi_choice',
        query__call_target__attribute='multi_choice',
    )
    def multi_choice(cls, call_target, **kwargs):
        setdefaults_path(kwargs, dict(
            bulk__model=kwargs.get('model'),
            query__model=kwargs.get('model'),
        ))
        return call_target(**kwargs)

    @classmethod
    @class_shortcut(
        bulk__call_target__attribute='text',
        query__call_target__attribute='text',
    )
    def text(cls, call_target, **kwargs):
        return call_target(**kwargs)

    @classmethod
    @class_shortcut
    def link(cls, call_target, **kwargs):
        # Shortcut for creating a cell that is a link. The URL is the result of calling `get_absolute_url()` on the object.
        def link_cell_url(table, column, row, value):
            del table, value
            r = getattr_path(row, column.attr)
            return r.get_absolute_url() if r else ''

        setdefaults_path(kwargs, dict(
            cell__url=link_cell_url,
        ))
        return call_target(**kwargs)

    @classmethod
    @class_shortcut
    def number(cls, call_target, **kwargs):
        # Shortcut for rendering a number. Sets the "rj" (as in "right justified") CSS class on the cell and header.
        return call_target(**kwargs)

    @classmethod
    @class_shortcut(
        call_target__attribute='number',
        query__call_target__attribute='float',
        bulk__call_target__attribute='float',
    )
    def float(cls, call_target, **kwargs):
        return call_target(**kwargs)

    @classmethod
    @class_shortcut(
        call_target__attribute='number',
        query__call_target__attribute='integer',
        bulk__call_target__attribute='integer',
    )
    def integer(cls, call_target, **kwargs):
        return call_target(**kwargs)

    @classmethod
    @class_shortcut(
        query__gui_op=':',
    )
    def substring(cls, call_target, **kwargs):
        return call_target(**kwargs)

    @classmethod
    @class_shortcut(
        query__call_target__attribute='date',
        query__op_to_q_op=lambda op: {'=': 'exact', ':': 'contains'}.get(op) or Q_OP_BY_OP[op],
        bulk__call_target__attribute='date',
    )
    def date(cls, call_target, **kwargs):
        return call_target(**kwargs)

    @classmethod
    @class_shortcut(
        query__call_target__attribute='datetime',
        query__op_to_q_op=lambda op: {'=': 'exact', ':': 'contains'}.get(op) or Q_OP_BY_OP[op],
        bulk__call_target__attribute='datetime',
    )
    def datetime(cls, call_target, **kwargs):
        return call_target(**kwargs)

    @classmethod
    @class_shortcut(
        query__call_target__attribute='time',
        query__op_to_q_op=lambda op: {'=': 'exact', ':': 'contains'}.get(op) or Q_OP_BY_OP[op],
        bulk__call_target__attribute='time',
    )
    def time(cls, call_target, **kwargs):
        return call_target(**kwargs)

    @classmethod
    @class_shortcut(
        query__call_target__attribute='email',
        bulk__call_target__attribute='email',
    )
    def email(cls, call_target, **kwargs):
        return call_target(**kwargs)

    @classmethod
    @class_shortcut(
        bulk__call_target__attribute='decimal',
        query__call_target__attribute='decimal',
    )
    def decimal(cls, call_target, **kwargs):
        return call_target(**kwargs)

    @classmethod
    @class_shortcut(
        call_target__attribute='multi_choice_queryset',
        bulk__call_target__attribute='many_to_many',
        query__call_target__attribute='many_to_many',
        cell__format=lambda value, **_: ', '.join(['%s' % x for x in value.all()]),
        data_retrieval_method=DataRetrievalMethods.prefetch,
    )
    def many_to_many(cls, call_target, model_field, **kwargs):
        setdefaults_path(
            kwargs,
            choices=model_field.remote_field.model.objects.all(),
            bulk__call_target__attribute='many_to_many',
            query__call_target__attribute='many_to_many',
            extra__django_related_field=True,
            model_field=model_field.remote_field,
        )
        return call_target(**kwargs)

    @classmethod
    @class_shortcut(
        call_target__attribute='choice_queryset',
        bulk__call_target__attribute='foreign_key',
        query__call_target__attribute='foreign_key',
        data_retrieval_method=DataRetrievalMethods.select,
    )
    def foreign_key(cls, call_target, model_field, **kwargs):
        setdefaults_path(
            kwargs,
            choices=model_field.foreign_related_fields[0].model.objects.all(),
            model_field=model_field.foreign_related_fields[0].model,
        )
        return call_target(**kwargs)


# TODO: why isn't this PagePart?
class BoundRow(object):
    """
    Internal class used in row rendering
    """

    def __init__(self, table, row, row_index):
        self.table: Table = table
        self.row: Any = row
        assert not isinstance(self.row, BoundRow)
        self.row_index = row_index
        self.parent = table
        self.name = 'row'
        self.template = evaluate(table.row.template, row=self.row, **table.evaluate_attribute_kwargs())
        self.extra = table.row.extra
        self.extra_evaluated = evaluate_strict_container(table.row.extra_evaluated, row=self.row, **table.evaluate_attribute_kwargs())
        self.attrs = table.row.attrs
        self.attrs = evaluate_attrs(self, table=table, row=row, bound_row=self)

    def __html__(self):
        if self.template:
            context = dict(bound_row=self, row=self.row, **self.table.context)
            return render_template(self.table.request(), self.template, context)

        return format_html('<tr{}>{}</tr>', self.attrs, self.render_cells())

    def render_cells(self):
        return mark_safe('\n'.join(bound_cell.__html__() for bound_cell in self))

    def __iter__(self):
        for column in self.table.rendered_columns.values():
            yield BoundCell(bound_row=self, column=column)

    def __getitem__(self, name):
        column = self.table.rendered_columns[name]
        return BoundCell(bound_row=self, column=column)

    def dunder_path(self):
        return self.parent.dunder_path() + '__row'


# TODO: make this a PagePart?
class BoundCell(object):

    def __init__(self, bound_row, column):
        assert column.include

        self.column = column
        self.bound_row = bound_row
        self.table = bound_row.table
        self.row = bound_row.row

    @property
    def value(self):
        if not hasattr(self, '_value'):
            self._value = evaluate_strict(
                self.column.cell.value,
                table=self.bound_row.table,
                declared_column=self.column.declared_column,
                row=self.bound_row.row,
                bound_row=self.bound_row,
                column=self.column,
            )
        return self._value

    @property
    def attrs(self):
        return evaluate_attrs(
            # TODO: fix this hack
            Struct(
                attrs=self.column.cell.attrs,
                dunder_path=lambda: self.column.dunder_path() + '__cell',
                name='cell',
            ),
            table=self.table,
            column=self.column,
            row=self.row,
            value=self.value,
        )

    @property
    def url(self):
        url = self.column.cell.url
        if callable(url):
            url = url(table=self.table, column=self.column, row=self.row, value=self.value)
        return url

    @property
    def url_title(self):
        url_title = self.column.cell.url_title
        if callable(url_title):
            url_title = url_title(table=self.table, column=self.column, row=self.row, value=self.value)
        return url_title

    def __html__(self):
        cell__template = self.column.cell.template
        if cell__template:
            context = dict(table=self.table, column=self.column, bound_row=self.bound_row, row=self.row, value=self.value, bound_cell=self)
            return render_template(self.table.request(), cell__template, context)

        return format_html('<td{}>{}</td>', self.attrs, self.render_cell_contents())

    def render_cell_contents(self):
        cell_contents = self.render_formatted()

        url = self.url
        if url:
            url_title = self.url_title
            cell_contents = format_html('<a{}{}>{}</a>',
                                        format_html(' href="{}"', url),
                                        format_html(' title="{}"', url_title) if url_title else '',
                                        cell_contents)
        return cell_contents

    def render_formatted(self):
        return evaluate_strict(self.column.cell.format, table=self.table, column=self.column, row=self.row, value=self.value)

    def __str__(self):
        return self.__html__()

    def __repr__(self):
        return "<%s column=%s row=%s>" % (self.__class__.__name__, self.column.declared_column, self.bound_row.row)  # pragma: no cover


class TemplateConfig(Struct, RefinableObject):
    template: str = Refinable()


class HeaderConfig(RefinableObject):
    attrs: Dict[str, Any] = Refinable()
    template: str = Refinable()
    extra: Dict[str, Any] = Refinable()


class RowConfig(RefinableObject):
    attrs: Dict[str, Any] = Refinable()
    template: str = Refinable()
    extra: Dict[str, Any] = Refinable()
    extra_evaluated: Dict[str, Any] = Refinable()


# TODO: make this a PagePart?
class Header(object):
    @dispatch(
        attrs=EMPTY,
    )
    def __init__(self, *, display_name, attrs, template, table, url=None, column=None, number_of_columns_in_group=None, index_in_group=None):
        self.table = table
        self.display_name = mark_safe(display_name)
        self.template = template
        self.url = url
        self.column = column
        self.number_of_columns_in_group = number_of_columns_in_group
        self.index_in_group = index_in_group
        self.attrs = attrs
        self.attrs = evaluate_attrs(self, table=table, column=column, header=self)

    @property
    def rendered(self):
        return render_template(self.table.request(), self.template, dict(header=self))

    def __repr__(self):
        return '<Header: %s>' % ('superheader' if self.column is None else self.column.name)

    def dunder_path(self):
        return self.table.dunder_path() + '__header'


def bulk__post_handler(table, form, **_):
    queryset = table.bulk_queryset()

    updates = {
        field.name: field.value
        for field in form.fields.values()
        if field.value is not None and field.value != '' and field.attr is not None
    }
    queryset.update(**updates)

    table.post_bulk_edit(table=table, queryset=queryset, updates=updates)

    return HttpResponseRedirect(form.request().META['HTTP_REFERER'])


# TODO: full PagePart?
class Paginator:
    def __init__(self, *, django_paginator, table, adjacent_pages=6):
        self.paginator = django_paginator
        self.table: Table = table
        self.adjacent_pages = adjacent_pages

        request = self.table.request()
        self.page_param_path = path_join(self.table.path(), 'page')
        page = request.GET.get(self.page_param_path) if request else None
        self.page = int(page) if page else 1

    def get_paginated_rows(self):
        return self.paginator.get_page(self.page).object_list

    def __html__(self):
        context = {}

        request = self.table.request()

        assert self.page != 0  # pages are 1-indexed!
        num_pages = self.paginator.num_pages
        foo = self.page
        if foo <= self.adjacent_pages:
            foo = self.adjacent_pages + 1
        elif foo > num_pages - self.adjacent_pages:
            foo = num_pages - self.adjacent_pages
        page_numbers = [
            n for n in
            range(self.page - self.adjacent_pages, foo + self.adjacent_pages + 1)
            if 0 < n <= num_pages
        ]

        get = request.GET.copy() if request is not None else {}

        if self.page_param_path in get:
            del get[self.page_param_path]

        context = {**context, **dict(
            extra=get and (get.urlencode() + "&") or "",
            page_numbers=page_numbers,
            show_first=1 not in page_numbers,
            show_last=num_pages not in page_numbers,
        )}

        page_obj = self.paginator.get_page(self.page)

        if self.paginator.num_pages > 1:
            context.update({
                'page_param_path': self.page_param_path,
                'is_paginated': self.paginator.num_pages > 1,
                'results_per_page': self.table.page_size,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'next': page_obj.next_page_number() if page_obj.has_next() else None,
                'previous': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'page': page_obj.number,
                'pages': self.paginator.num_pages,
                'hits': self.paginator.count,
            })
        else:
            return ''

        return render_template(
            request=self.table.request(),
            template=self.table.paginator_template,
            context=context,
        )

    def __str__(self):
        return self.__html__()


@no_copy_on_bind
@declarative(Column, '_columns_dict')
@with_meta
class Table(PagePart):
    """
    Describe a table. Example:

    .. code:: python

        class FooTable(Table):
            a = Column()
            b = Column()

            class Meta:
                sortable = False
                attrs__style = 'background: green'

    """

    bulk_filter: Namespace = Refinable()
    bulk_exclude: Namespace = Refinable()
    sortable: bool = Refinable()
    query_from_indexes: bool = Refinable()
    default_sort_order = Refinable()
    attrs: Dict[str, Any] = Refinable()
    template: Union[str, Template] = Refinable()
    row = Refinable()
    # TODO: this is only used for filter__template, we should change this to just filter_template, or even query_template
    filter: Namespace = Refinable()
    header = Refinable()
    model: Type['django.db.models.Model'] = Refinable()
    rows = Refinable()
    columns = Refinable()
    bulk: Namespace = Refinable()
    endpoint: Namespace = Refinable()
    superheader: Namespace = Refinable()
    paginator: Paginator = Refinable()
    paginator_template: str = Refinable()
    page_size: int = Refinable()
    actions_template: Union[str, Template] = Refinable()
    member_class = Refinable()
    form_class: Type[Form] = Refinable()
    query_class: Type[Query] = Refinable()
    action_class: Type[Action] = Refinable()

    class Meta:
        member_class = Column
        form_class = Form
        query_class = Query
        action_class = Action
        endpoint__tbody = (lambda table, key, value: {'html': table.__html__(template='tri_table/table_container.html')})

        attrs = {'data-endpoint': lambda table, **_: DISPATCH_PREFIX + path_join(table.path(), 'tbody')}
        query__default_child = True
        query__form__default_child = True

    def children(self):
        return Struct(
            query=self.query,  # TODO: this is a property which we should try to remove
            bulk=self.bulk_form,  # TODO: this is a property which we should try to remove, also different from the line above

            columns=self.columns,
            # TODO: paginator?

            # TODO: this can have name collisions with the keys above
            **setup_endpoint_proxies(self)
        )

    @staticmethod
    @refinable
    def preprocess_rows(rows, **_):
        return rows

    @staticmethod
    @refinable
    def preprocess_row(table, row, **_):
        del table
        return row

    @staticmethod
    @refinable
    def post_bulk_edit(table, queryset, updates):
        pass

    @dispatch(
        columns=EMPTY,
        bulk_filter={},
        bulk_exclude={},
        sortable=True,
        default_sort_order=None,
        attrs=EMPTY,
        template='iommi/table/list.html',
        row__attrs__class=EMPTY,
        row__attrs={'data-pk': lambda row, **_: getattr(row, 'pk', None)},
        row__template=None,
        row__extra=EMPTY,
        row__extra_evaluated=EMPTY,
        filter__template='iommi/query/form.html',
        header__template='iommi/table/table_header_rows.html',
        paginator_template='iommi/table/paginator.html',
        paginator__call_target=Paginator,

        actions=EMPTY,
        actions_template='iommi/form/actions.html',
        query=EMPTY,
        bulk=EMPTY,
        page_size=DEFAULT_PAGE_SIZE,

        superheader__attrs__class__superheader=True,
        superheader__template='iommi/table/header.html',
    )
    def __init__(self, *, columns: Namespace = None, _columns_dict=None, model=None, rows=None, filter=None, bulk=None, header=None, query=None, row=None, instance=None, actions: Namespace = None, default_child=None, **kwargs):
        """
        :param rows: a list or QuerySet of objects
        :param columns: (use this only when not using the declarative style) a list of Column objects
        :param attrs: dict of strings to string/callable of HTML attributes to apply to the table
        :param row__attrs: dict of strings to string/callable of HTML attributes to apply to the row. Callables are passed the row as argument.
        :param row__template: name of template (or `Template` object) to use for rendering the row
        :param bulk_filter: filters to apply to the `QuerySet` before performing the bulk operation
        :param bulk_exclude: exclude filters to apply to the `QuerySet` before performing the bulk operation
        :param sortable: set this to `False` to turn off sorting for all columns
        """
        assert isinstance(columns, dict)

        model, rows = model_and_rows(model, rows)

        self._actions_unapplied_data = {}
        self.declared_actions = collect_members(items=actions, cls=self.get_meta().action_class, unapplied_config=self._actions_unapplied_data)
        self.actions = None

        self._columns_unapplied_data = {}
        self.declared_columns: Dict[str, Column] = collect_members(items=columns, items_dict=_columns_dict, cls=self.get_meta().member_class, unapplied_config=self._columns_unapplied_data)
        self.columns = None
        self.rendered_columns = None

        self.instance = instance

        super(Table, self).__init__(
            model=model,
            rows=rows,
            filter=TemplateConfig(**filter),
            header=HeaderConfig(**header),
            row=RowConfig(**row),
            bulk=bulk,
            **kwargs
        )

        if model and self.extra.get('model_verbose_name') is None:
            # noinspection PyProtectedMember
            self.extra.model_verbose_name = model._meta.verbose_name_plural.replace('_', ' ').capitalize()

        self.default_child = default_child

        self.query_args = query
        self._query: Query = None
        self._query_form: Form = None
        self._query_error: List[str] = None

        self._bulk_form: Form = None
        self.header_levels = None

    def render_actions(self):
        actions, grouped_actions = group_actions(self.actions)
        return render_template(
            self.request(),
            self.actions_template,
            dict(
                actions=actions,
                grouped_actions=grouped_actions,
                table=self,
            ))

    def render_header(self):
        return render_template(self.request(), self.header.template, self.context)

    def render_filter(self):
        if not self.query_form:
            return ''
        # TODO: why are we using self.filter.template here? and all this complex stuff generally, when we should be able to just render the query in the template like {{ table.query }}?
        return render_template(self.request(), self.filter.template, self.context)

    def _prepare_auto_rowspan(self):
        auto_rowspan_columns = [column for column in self.columns.values() if column.auto_rowspan]

        if auto_rowspan_columns:
            self.rows = list(self.rows)
            no_value_set = object()
            for column in auto_rowspan_columns:
                rowspan_by_row = {}  # cells for rows in this dict are displayed, if they're not in here, they get style="display: none"
                prev_value = no_value_set
                prev_row = no_value_set
                for bound_row in self.bound_rows():
                    value = BoundCell(bound_row, column).value
                    if prev_value != value:
                        rowspan_by_row[id(bound_row.row)] = 1
                        prev_value = value
                        prev_row = bound_row.row
                    else:
                        rowspan_by_row[id(prev_row)] += 1

                orig_style = column.cell.attrs.get('style')

                def rowspan(row, **_):
                    return rowspan_by_row[id(row)] if id(row) in rowspan_by_row else None

                def style(row, **_):
                    return 'display: none%s' % ('; ' + orig_style if orig_style else '') if id(row) not in rowspan_by_row else orig_style

                assert 'rowspan' not in column.cell.attrs
                dict.__setitem__(column.cell.attrs, 'rowspan', rowspan)
                dict.__setitem__(column.cell.attrs, 'style', style)

    def _prepare_sorting(self):
        request = self.request()
        if request is None:
            return

        order = request.GET.get(path_join(self.path(), 'order'), self.default_sort_order)
        if order is not None:
            is_desc = order[0] == '-'
            order_field = is_desc and order[1:] or order
            tmp = [x for x in self.columns.values() if x.name == order_field]
            if len(tmp) == 0:
                return  # Unidentified sort column
            sort_column = tmp[0]
            order_args = evaluate_strict(sort_column.sort_key, column=sort_column)
            order_args = isinstance(order_args, list) and order_args or [order_args]

            if sort_column.sortable:
                if isinstance(self.rows, list):
                    order_by_on_list(self.rows, order_args[0], is_desc)
                else:
                    if not settings.DEBUG:
                        # We should crash on invalid sort commands in DEV, but just ignore in PROD
                        # noinspection PyProtectedMember
                        valid_sort_fields = {x.name for x in self.model._meta.get_fields()}
                        order_args = [order_arg for order_arg in order_args if order_arg.split('__', 1)[0] in valid_sort_fields]
                    order_args = ["%s%s" % (is_desc and '-' or '', x) for x in order_args]
                    self.rows = self.rows.order_by(*order_args)

    def _prepare_headers(self):
        prepare_headers(self, self.rendered_columns.values())

        for column in self.rendered_columns.values():
            evaluate_members(
                column,
                [
                    'superheader',
                    'header',
                ],
                **self.evaluate_attribute_kwargs()
            )

        superheaders = []
        subheaders = []

        # The id(header) and stuff is to make None not be equal to None in the grouping
        for _, group_iterator in groupby(self.rendered_columns.values(), key=lambda header: header.group or id(header)):
            columns_in_group = list(group_iterator)
            group_name = columns_in_group[0].group

            number_of_columns_in_group = len(columns_in_group)

            superheaders.append(Header(
                display_name=group_name or '',
                table=self,
                attrs=self.superheader.attrs,
                attrs__colspan=number_of_columns_in_group,
                template=self.superheader.template,
            ))

            for i, column in enumerate(columns_in_group):
                subheaders.append(
                    Header(
                        display_name=column.display_name,
                        table=self,
                        attrs=column.header.attrs,
                        template=column.header.template,
                        url=column.url,
                        column=column,
                        number_of_columns_in_group=number_of_columns_in_group,
                        index_in_group=i,
                    )
                )

        if all(c.display_name == '' for c in superheaders):
            superheaders = None

        if superheaders is None:
            self.header_levels = [subheaders]
        else:
            self.header_levels = [superheaders, subheaders]

    # TODO: clear out as many as these properties as we can
    @property
    def query(self) -> Query:
        assert self._is_bound
        return self._query

    @property
    def query_form(self) -> Form:
        assert self._is_bound
        return self._query_form

    @property
    def query_error(self) -> List[str]:
        assert self._is_bound
        return self._query_error

    @property
    def bulk_form(self) -> Form:
        assert self._is_bound
        return self._bulk_form

    def on_bind(self) -> None:
        bind_members(self, name='actions')
        bind_members(self, name='columns')

        evaluate_member(self, 'sortable', **self.evaluate_attribute_kwargs())  # needs to be done first because _prepare_headers depends on it
        self._prepare_sorting()

        evaluate_member(self, 'model', strict=False, **self.evaluate_attribute_kwargs())

        for column in self.columns.values():
            # Special case for entire table not sortable
            if not self.sortable:
                column.sortable = False

            # Special case for automatic query config
            if self.query_from_indexes and column.model_field and getattr(column.model_field, 'db_index', False):
                column.query.include = True
                column.query.form.include = True

        self.rendered_columns = Struct({name: column for name, column in self.columns.items() if column.render_column})

        self._prepare_headers()
        evaluate_members(
            self,
            [
                'bulk_filter',
                'bulk_exclude',
                'row',
                'filter',
                '_query',
                'bulk',
            ],
            **self.evaluate_attribute_kwargs()
        )
        self.attrs = evaluate_attrs(self, **self.evaluate_attribute_kwargs())

        if self.model:

            def generate_variables():
                for column in self.columns.values():
                    # TODO: column.query.include... is this evaluated here?
                    if column.query.include:
                        query_namespace = setdefaults_path(
                            Namespace(),
                            column.query,
                            call_target__cls=self.get_meta().query_class.get_meta().member_class,
                            model=self.model,
                            name=column.name,
                            attr=column.attr,
                            form__display_name=column.display_name,
                            form__call_target__cls=self.get_meta().query_class.get_meta().form_class.get_meta().member_class,
                        )
                        if 'call_target' not in query_namespace['call_target'] and query_namespace['call_target'].get(
                                'attribute') == 'from_model':
                            query_namespace['field_name'] = column.attr
                        yield query_namespace()

            variables = Struct({x.name: x for x in generate_variables()})

            self._query = self.get_meta().query_class(
                _variables_dict=variables,
                name='query',
                **self.query_args
            )
            self._query.bind(parent=self)
            self._query_form = self._query.form if self._query.variables else None

            self._query_error = ''
            if self._query_form:
                try:
                    q = self.query.to_q()
                    if q:
                        self.rows = self.rows.filter(q)
                except QueryException as e:
                    self._query_error = str(e)

            def generate_bulk_fields():
                for column in self.columns.values():
                    if column.bulk.include:
                        bulk_namespace = setdefaults_path(
                            Namespace(),
                            column.bulk,
                            call_target__cls=self.get_meta().form_class.get_meta().member_class,
                            model=self.model,
                            name=column.name,
                            attr=column.attr,
                            display_name=column.display_name,
                            required=False,
                            empty_choice_tuple=(None, '', '---', True),
                        )
                        if 'call_target' not in bulk_namespace['call_target'] and bulk_namespace['call_target'].get('attribute') == 'from_model':
                            bulk_namespace['field_name'] = column.attr
                        yield bulk_namespace()

            bulk_fields = Struct({x.name: x for x in generate_bulk_fields()})
            if bulk_fields:
                bulk_fields._all_pks_ = self.get_meta().form_class.get_meta().member_class.hidden(name='_all_pks_', attr=None, initial='0', required=False)

                self._bulk_form = self.get_meta().form_class(
                    fields=bulk_fields,
                    name='bulk',
                    post_handler=bulk__post_handler,
                    actions__submit__include=False,
                    **self.bulk
                )
                self._bulk_form.bind(parent=self)
                assert 'bulk' not in self.actions
                self.actions['bulk'] = Action.submit(name='bulk', attrs__value='Bulk change').bind(parent=self)
            else:
                self._bulk_form = None

        if isinstance(self.rows, QuerySet):
            prefetch = [x.attr for x in self.columns.values() if x.data_retrieval_method == DataRetrievalMethods.prefetch and x.attr]
            select = [x.attr for x in self.columns.values() if x.data_retrieval_method == DataRetrievalMethods.select and x.attr]
            if prefetch:
                self.rows = self.rows.prefetch_related(*prefetch)
            if select:
                self.rows = self.rows.select_related(*select)

        request = self.request()
        # TODO: I paginate only when I have a request... this is a bit weird, but matches old behavior and the tests assume this for now
        if self.page_size and request:
            try:
                self.page_size = int(request.GET.get('page_size', self.page_size)) if request else self.page_size
            except ValueError:
                pass

            if isinstance(self.paginator.call_target, type) and issubclass(self.paginator.call_target, DjangoPaginator):
                django_paginator = self.paginator(self.rows, self.page_size)
            elif isinstance(self.paginator.call_target, DjangoPaginator):
                django_paginator = self.paginator
            else:
                assert isinstance(self.paginator, Namespace)
                django_paginator = DjangoPaginator(self.rows, self.page_size)
            self.paginator = Paginator(table=self, django_paginator=django_paginator)

            try:
                self.rows = self.paginator.get_paginated_rows()
            except (InvalidPage, ValueError):
                raise Http404

        self._prepare_auto_rowspan()

        self.extra_evaluated = evaluate_strict_container(self.extra_evaluated, **self.evaluate_attribute_kwargs())

    def _evaluate_attribute_kwargs(self):
        return dict(table=self)

    def bound_rows(self):
        assert self._is_bound
        for i, row in enumerate(self.preprocess_rows(rows=self.rows, table=self)):
            row = self.preprocess_row(table=self, row=row)
            yield BoundRow(table=self, row=row, row_index=i)

    def render_tbody(self):
        return mark_safe('\n'.join([bound_row.__html__() for bound_row in self.bound_rows()]))

    @classmethod
    @dispatch(
        columns=EMPTY,
    )
    def columns_from_model(cls, columns, **kwargs):
        return create_members_from_model(
            member_params_by_member_name=columns,
            default_factory=cls.get_meta().member_class.from_model,
            **kwargs
        )

    @classmethod
    @dispatch(
        columns=EMPTY,
    )
    def from_model(cls, rows=None, model=None, columns=None, instance=None, include=None, exclude=None, extra_columns=None, **kwargs):
        """
        Create an entire form based on the columns of a model. To override a column parameter send keyword arguments in the form
        of "the_name_of_the_columns__param". For example:

        .. code:: python

            class Foo(Model):
                foo = IntegerField()

            Table.from_model(request=request, model=Foo, columns__foo__help_text='Overridden help text')

        :param include: columns to include. Defaults to all
        :param exclude: columns to exclude. Defaults to none (except that AutoField is always excluded!)

        """
        model, rows = model_and_rows(model, rows)
        assert model is not None or rows is not None, "model or rows must be specified"
        columns = cls.columns_from_model(model=model, include=include, exclude=exclude, extra=extra_columns, columns=columns)
        return cls(rows=rows, model=model, instance=instance, columns=columns, **kwargs)

    def bulk_queryset(self):
        queryset = self.model.objects.all() \
            .filter(**self.bulk_filter) \
            .exclude(**self.bulk_exclude)

        if self.request().POST.get('_all_pks_') == '1':
            return queryset
        else:
            pks = [key[len('pk_'):] for key in self.request().POST if key.startswith('pk_')]
            return queryset.filter(pk__in=pks)

    @dispatch(
        render=render_template,
        context=EMPTY,
    )
    def __html__(self, *, context=None, render=None):
        assert self._is_bound

        if not context:
            context = {}
        else:
            context = context.copy()

        context['table'] = self
        context['bulk_form'] = self.bulk_form
        context['query'] = self.query
        context['iommi_query_error'] = self.query_error

        request = self.request()

        assert self.rows is not None
        context['paginator'] = self.paginator

        self.context = context

        if self.query_form and not self.query_form.is_valid():
            self.rows = None
            self.context['invalid_form_message'] = mark_safe('<i class="fa fa-meh-o fa-5x" aria-hidden="true"></i>')

        # TODO: what if self.template is a Template?
        return render(request=request, template=self.template, context=self.context)

    @dispatch(
        parts=EMPTY,
    )
    def as_page(self, *, title=None, parts=None, default_child=True):

        # TODO: clean this up
        if title is None:
            title = self.extra.get('model_verbose_name', '')

        self.default_child = default_child

        from iommi.page import (
            Page,
            html,
        )
        return Page(
            # TODO: do I need to do this pop manually? Won't this be handled by collect_members/bind_members?
            parts__title=html.h1(title, **parts.pop('title', {})),
            # TODO: we should use the name given here, not hard code "table"
            parts__table=self,
            parts=parts,
            default_child=True,
        )
