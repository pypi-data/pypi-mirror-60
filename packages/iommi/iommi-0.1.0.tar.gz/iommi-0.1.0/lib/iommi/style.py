from collections import defaultdict
from typing import (
    List,
    Type,
)

from tri_declarative import (
    Namespace,
    RefinableObject,
    get_shortcuts_by_name,
)


# TODO: This system is extremely powerful. It can overwrite anything and everything. It should probably only be applicable to some specifically "stylable" parts.

def _style_name_for_class(cls):
    return cls.__name__.rpartition('.')[-1]  # this converts iommi.form.Form to just Form


def class_names_for(cls):
    from iommi import PagePart  # avoid circular import

    for base_class in reversed(cls.mro()):
        if base_class in (object, PagePart, RefinableObject):
            continue
        yield _style_name_for_class(base_class)


def recursive_namespace(d):
    if isinstance(d, dict):
        return Namespace({k: recursive_namespace(v) for k, v in d.items()})
    else:
        return d


class Style:
    def __init__(self, *bases, **kwargs):
        self.config = Namespace(*[x.config for x in bases], recursive_namespace(kwargs))

    def component(self, obj):
        result = Namespace()
        for class_name in class_names_for(obj.__class__):
            if class_name in self.config:
                config = Namespace(self.config.get(class_name, {}))
                shortcuts_config = Namespace(config.pop('shortcuts', {}))
                result.update(config)

                for shortcut_name in reversed(getattr(obj, '__tri_declarative_shortcut_stack', [])):
                    result = Namespace(result, shortcuts_config.get(shortcut_name, {}))
        return result


base = Style(
    Form=dict(
        template='iommi/form/form.html',
        actions_template='iommi/form/actions.html',
    ),
    Field=dict(
        shortcuts=dict(
            textarea=dict(
                input__template='iommi/form/textarea.html',
            ),
            boolean=dict(
                input__attrs__type='checkbox',
            ),
            choice=dict(
                input__template='iommi/form/choice.html',
                input__attrs__value=None,
                input__attrs__type=None,
            ),
            choice_queryset=dict(
                input__template='iommi/form/choice_select2.html',
            ),
            radio=dict(
                input__template='iommi/form/radio.html',
            ),
            file=dict(
                input__template='iommi/form/file.html',
            ),
            heading=dict(
                template='iommi/form/heading.html',
            ),
        ),
        input__attrs__type='text',
        input__tag='input',
        input__name='input',
        label__tag='label',
        label__name='label',
    ),
    Column=dict(
        shortcuts=dict(
            select=dict(
                header__attrs__title='Select all',
                header__attrs__class__thin=True,
                header__attrs__class__nopad=True,
                cell__attrs__class__cj=True,

            ),
            number=dict(
                cell__attrs__class__rj=True,
            ),
        )
    ),
    # TODO: this is a bit bonkers
    Query__form__attrs__id='iommi_query_form',
)

test = Style(
    base,
    Field=dict(
        shortcuts=dict(
            boolean=dict(
                template='iommi/form/bootstrap/row_checkbox.html',
            ),
        ),
        template='iommi/form/bootstrap/row.html',
        errors__template='iommi/form/bootstrap/errors.html',
    ),
    Table=dict(
        attrs__class__table=True,
    ),
)

bootstrap = Style(
    base,
    Field=dict(
        shortcuts=dict(
            boolean=dict(
                input__attrs__class={'form-check-input': True, 'form-control': False},
                attrs__class={'form-check': True},
                label__attrs__class={'form-check-label': True},
                template='iommi/form/bootstrap/row_checkbox.html',
            ),
        ),
        attrs__class={
            'form-group': True,
        },
        input__attrs__class={
            'form-control': True,
        },
        errors__attrs__class={'invalid-feedback': True},
        template='iommi/form/bootstrap/row.html',
        errors__template='iommi/form/bootstrap/errors.html',
    ),
    Action=dict(
        shortcuts=dict(
            button__attrs__class={
                'btn': True,
                'btn-primary': True,
            },
            delete__attrs__class={
                'btn-primary': False,
                'btn-danger': True,
            },
        ),
    ),
    Table=dict(
        attrs__class__table=True,
    ),
    Column=dict(
        header__attrs__class={'text-nowrap': True},
    ),
    Query__form__style='bootstrap_horizontal',

    Column__shortcuts__number__cell__attrs__class__rj=True,
)

bootstrap_horizontal = Style(
    bootstrap,
    Field=dict(
        shortcuts=dict(
            boolean__label__attrs__class={
                'col-form-label': True,
            },
        ),
        attrs__class={
            'form-group': False,
            'col-sm-3': True,
            'my-1': True,
        },
        errors__attrs__class={'invalid-feedback': True},
        errors__template='iommi/form/bootstrap/errors.html',
    ),
    Form__attrs__class={
        'align-items-center': True,
    }
)

_styles = {}


def register_style(name, conf):
    assert name not in _styles
    _styles[name] = conf


register_style('base', base)
register_style('test', test)
register_style('bootstrap', bootstrap)
register_style('bootstrap_horizontal', bootstrap_horizontal)


def get_style(name):
    return _styles[name]


def apply_style_recursively(*, style_data, obj):
    if isinstance(obj, dict):
        result = Namespace(style_data, obj)
        obj.clear()
        obj.update(**result)
    else:
        for k, v in style_data.items():
            if isinstance(v, dict):
                apply_style_recursively(style_data=v, obj=getattr(obj, k))
            else:
                if getattr(obj, k) is None:
                    setattr(obj, k, v)


def get_style_for_object(style, self):
    return get_style(style).component(self)


class InvalidStyleConfigurationException(Exception):
    pass


def validate_styles(*, classes: List[Type] = None):
    from iommi import (
        Field,
        Form,
        Column,
        Table,
        Variable,
        Query,
        Action,
    )
    classes = (classes or []) + [
        Field,
        Form,
        Column,
        Table,
        Variable,
        Query,
        Action,
    ]

    # We can have multiple classes called Field. In fact that's the recommended way to use iommi!
    classes_by_name = defaultdict(list)
    for cls in classes:
        for cls_name in class_names_for(cls):
            classes_by_name[cls_name].append(cls)

    # This will functionally merge separate trees of class inheritance. So it produces a list of all shortcuts on all classes called something.Field.
    shortcuts_available_by_class_name = defaultdict(set)
    for cls_name, classes in classes_by_name.items():
        for cls in classes:
            shortcuts_available_by_class_name[cls_name].update(get_shortcuts_by_name(cls).keys())

    invalid_class_names = []
    non_existent_shortcut_names = []
    for style_name, style in _styles.items():
        for cls_name, config in style.config.items():
            # First validate the top level classes
            if cls_name not in classes_by_name:
                invalid_class_names.append((style_name, cls_name))
                continue

            # Then validate the shortcuts
            for shortcut_name in config.get('shortcuts', {}).keys():
                if shortcut_name not in shortcuts_available_by_class_name[cls_name]:
                    non_existent_shortcut_names.append((style_name, cls_name, shortcut_name))

    if invalid_class_names or non_existent_shortcut_names:
        invalid_class_names_str = '\n'.join(
            f'    Style: {style_name} - class: {cls_name}'
            for style_name, cls_name in invalid_class_names
        )
        if invalid_class_names_str:
            invalid_class_names_str = 'Invalid class names:\n' + invalid_class_names_str
        invalid_shortcut_names_str = '    \n'.join(
            f'    Style: {style_name} - class: {cls_name} - shortcut: {shortcut_name}'
            for style_name, cls_name, shortcut_name in non_existent_shortcut_names
        )
        if invalid_shortcut_names_str:
            invalid_shortcut_names_str = 'Invalid shortcut names:\n' + invalid_shortcut_names_str
        raise InvalidStyleConfigurationException('\n\n'.join([invalid_class_names_str, invalid_shortcut_names_str]))
