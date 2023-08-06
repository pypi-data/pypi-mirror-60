from collections import OrderedDict
from copy import deepcopy
from typing import Any, Collection, Type, Iterable, TypeVar

from django.db.models import Model
from django.forms import Form, ModelForm, Field, Widget, BaseFormSet
from django.forms.forms import DeclarativeFieldsMetaclass, BaseForm
from django.forms.models import ModelFormMetaclass, BaseInlineFormSet, BaseModelFormSet
from django.template.loader import render_to_string
from django.utils.timezone import now as tz_now

from flex_forms.components import TemplateElement, StaticFlexField, FlexDataArrayType, FormError, \
    FormErrorType, BaseStaticFlexField
from flex_forms.utils import format_date, Collector, safety_get_attribute, camel_to_snake

ModelType = TypeVar('ModelType', bound=Model)
ModelFieldType = TypeVar('ModelFieldType', bound=Field)


# Service classes

class FlexFormParameters:
    """
    Flex form additional parameters collection.
    """

    REQUIRED_TEXT = 'required_text'
    ICON = 'icon'
    SHOW_ERRORS = 'show_errors'
    WRAPPER_TEMPLATE = 'wrapper_template'
    FIELD_GROUP_CLASS = 'field_group_class'
    READONLY = 'readonly'
    DISABLED = 'disabled'


# endregion


# region Form methods mixins

class CommonFormMethods:
    """
    Extends forms functionality with some useful methods.
    """

    DISABLED_FIELD_CSS_CLASS: str = 'flex-form-disabled-field'

    def disable_fields(self, *fields_to_process, by_css_class_only: bool = False) -> None:
        # disable fields by 'disable' attribute or special css-class.
        for field in fields_to_process:
            if field in self.fields:
                field_obj = self.fields[field]
                self.add_fields_classes(
                    field, fields_classes=(self.DISABLED_FIELD_CSS_CLASS,)
                )
                if not by_css_class_only:
                    field_obj.disabled = True

    def add_fields_classes(self, *fields_to_process, fields_classes: Collection[str]) -> None:
        # adds classes to group of fields.
        for field in fields_to_process:
            if field in self.fields:
                widget_classes = self.fields[field].widget.attrs.get('class', '').split(' ')
                widget_classes += fields_classes
                self.fields[field].widget.attrs['class'] = ' '.join(set(widget_classes))

    def set_fields_attr(self, *fields_to_process, attr: str, value: Any, reverse: bool = False) -> None:
        if not reverse:
            for field in fields_to_process:
                if field in self.fields:
                    setattr(self.fields[field], attr, value)
        else:
            for field in self.fields:
                if field not in fields_to_process:
                    setattr(self.fields[field], attr, value)

    def set_widget_attr(self, *fields_to_process, attr: str, value: Any, reverse: bool = False) -> None:
        if not reverse:
            for field in fields_to_process:
                if field in self.fields:
                    self.fields[field].widget.attrs[attr] = value
        else:
            for field in self.fields:
                if field not in fields_to_process:
                    self.fields[field].widget.attrs[attr] = value

    def del_fields(self, *fields_to_process, reverse: bool = False) -> None:
        if not reverse:
            for field in fields_to_process:
                if field in self.fields:
                    del self.fields[field]
        else:
            for field in self.fields:
                if field not in fields_to_process:
                    del self.fields[field]


class ModelFormMethods:
    """
    Mixin such as CommonFormMethods but only for model forms.
    """

    def check_for_unique(self, *fields_to_process, error_message: str, error_field: str = None) -> None:
        # check instance for unique by fields values.
        filter_kwargs = {
            field_name: self.cleaned_data.get(field_name)
            for field_name in fields_to_process if self.cleaned_data.get(field_name, None) is not None
        }
        if len(filter_kwargs) == len(fields_to_process):
            same_objects = self.Meta.model.objects.filter(**filter_kwargs)
            if self.instance_exists:
                same_objects = same_objects.exclude(id=self.instance.id)
            if same_objects.exists():
                self.add_error(error_field, error_message)

    @property
    def instance_exists(self) -> bool:
        instance_exists = False
        if self.instance and self.instance.id:
            instance_exists = True
        return instance_exists


# endregion


# region Mixins

class StyledFormMixin(CommonFormMethods):
    """
    Mixin to style normal and model forms and extend their functionality.
    """

    _js_class_prefix: str = 'js-field_'
    _js_class_postfix: str = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_prefix()

    def _set_prefix(self) -> None:
        for field_name, field in self.get_field_items():
            if self._js_class_prefix or self._js_class_postfix:
                css_class = f'{self._js_class_prefix}{field_name}{self._js_class_postfix}'
                self.add_fields_classes(field_name, fields_classes=[css_class])

    def get_field_items(self) -> tuple:
        return self.fields.copy().items()

    def limit_max_date(self, field, date=None) -> None:
        if date is None:
            date = tz_now().date()
        field.widget.attrs.update({'data-max-date': format_date(date)})

    def limit_min_date(self, field, date=None) -> None:
        if date is None:
            date = tz_now().date()
        field.widget.attrs.update({'data-min-date': format_date(date)})


class UserFormKwargsMixin:
    """
    Adds the user to the template context. Use with UserFormKwargsMixin for views.
    """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class FormObjectContextMixin:
    """
    An extra context mixin that passes the keyword arguments received by
    get_context_data() as the form context.
    """

    extra_context: dict = {}

    def get_context_data(self, **kwargs) -> dict:
        if self.extra_context:
            kwargs.update(self.extra_context)
        return kwargs


class TemplateFormObjectContextMixin(FormObjectContextMixin, TemplateElement):
    """
    Adds html attributes to class and template context.
    """

    css_classes: list = []
    html_params: dict = {}

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context.update({
            'html_params': self.prepare_html_params(self.get_form_html_params())
        })
        return context

    def get_form_html_params(self) -> dict:
        # add a class as an HTML parameter, if one exists.
        html_params = self.html_params
        if self.css_classes:
            prepared_css_classes = self.prepare_css_classes(self.get_form_css_classes())
            html_params.update({'class': prepared_css_classes})
        return html_params

    def get_form_css_classes(self) -> list:
        return self.css_classes


class TemplateObjectMixin(TemplateFormObjectContextMixin):
    """
    Adds support for rendering a flex object (flex form / formset or static fieldset) with a custom template.
    """

    template_name: str = None
    context_object_name: str = None

    def _render(self) -> str:
        return self._get_template_or_string(self.template_name, self.get_context_data())

    def _get_template_or_string(self, template_name_or_string: str, context_data: dict = None) -> str:
        if template_name_or_string.endswith('.html'):
            return render_to_string(template_name_or_string, context_data or {})
        return template_name_or_string

    def get_template_name(self) -> str:
        return self.template_name

    def get_context_data(self, **kwargs) -> dict:
        return super().get_context_data(**{self.context_object_name: self, **kwargs})

    def as_flex(self) -> str:
        return self._render()


class TemplateFlexObjectMixin(TemplateObjectMixin):

    flex_type: str = None

    def as_flex(self) -> str:
        return self._render()


class DetachedFormObjectMediaMixin:

    @property
    def media_css(self):
        return self.media['css']

    @property
    def media_js(self):
        return self.media['js']


class FieldWrapperMixin(TemplateFlexObjectMixin):
    """
    Mixin which provides some methods for wrapping field widget templates by custom html-wrappers.
    """

    _row_str: str = 'flex_forms/blocks/row.html'
    _block_str: str = 'flex_forms/blocks/block.html'

    grid: dict = {}

    @property
    def row_str(self, context_data: dict = None) -> str:
        return self._get_template_or_string(self._row_str, context_data)

    @property
    def block_str(self, context_data: dict = None) -> str:
        return self._get_template_or_string(self._block_str, context_data)

    def get_grid(self) -> dict:
        return self.grid


class FlexTemplateFormMixin:
    """
    Mixin for rendering forms as flex forms.
    """

    _DEFAULT = 'default'
    _CHECKBOX_INPUT = 'CheckboxInput'
    _CHECKBOX_MULTI = 'CheckboxSelectMultiple'
    _RADIO_SELECT = 'RadioSelect'

    _EXTRA_WIDGETS = (
        _CHECKBOX_INPUT,
        _CHECKBOX_MULTI,
        _RADIO_SELECT
    )

    _fields_wrapper_templates: dict = {
        _DEFAULT: 'flex_forms/fields/generic.html',
        _CHECKBOX_INPUT: 'flex_forms/fields/checkbox.html',
        _CHECKBOX_MULTI: 'flex_forms/fields/checkbox_multi.html',
        _RADIO_SELECT: 'flex_forms/fields/radio.html'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_fields_wrapper_template_name()

    @classmethod
    def _get_widget_base_class(cls, field_widget: Widget) -> str:
        base_class = None
        if field_widget:
            base_classes = [fidget_class.__name__ for fidget_class in field_widget.__class__.__mro__]
            classes_intersection = set(cls._EXTRA_WIDGETS) & set(base_classes)
            if classes_intersection:
                base_class = classes_intersection.pop()
        return base_class

    def _set_fields_wrapper_template_name(self) -> None:
        # set wrapper_template to every form field in according to widget class.
        for field_name, field in getattr(self, 'fields', {}).items():
            widget = field.widget
            if FlexFormParameters.WRAPPER_TEMPLATE not in widget.attrs.keys():
                widget.attrs[FlexFormParameters.WRAPPER_TEMPLATE] = self.get_field_wrapper_template(field)

    def get_field_wrapper_template(self, field: Type[Field]) -> str:
        widget_class = self._get_widget_base_class(field.widget) or self._DEFAULT
        return self._fields_wrapper_templates.get(widget_class)


class FormObjectButtonsMixin:
    """
    Adds buttons to the form object context.
    """

    buttons: list = []

    def get_buttons(self) -> list:
        return self.buttons

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context.update(dict(
            buttons=self.get_buttons()
        ))
        return context


class StaticFieldsSupportMixin:
    """
    Adds static_fields support to forms or static fieldsets.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_fieldset = deepcopy(self.static_class_fields)


class FlexFormMixin(StyledFormMixin,
                    UserFormKwargsMixin,
                    FieldWrapperMixin,
                    FlexTemplateFormMixin,
                    DetachedFormObjectMediaMixin,
                    StaticFieldsSupportMixin):
    """
    The main mixin for converting a normal form / model form into a flex form.
    """

    flex_type = 'form'
    template_name = 'flex_forms/forms/generic_form.html'
    context_object_name = 'form'
    html_params = {'method': 'POST', 'action': '/'}


class FlexFormsetMixin(TemplateFlexObjectMixin):
    """
    Mixin such as FlexFormMixin - converts formset into a flex formset.
    """

    flex_type = 'formset'
    template_name = 'flex_forms/forms/generic_formset.html'
    context_object_name = 'formset'
    html_params = {'method': 'POST', 'action': '/'}


class StaticFieldsetMixin(FieldWrapperMixin, StaticFieldsSupportMixin):
    """
    Converts object to StaticFieldset.
    """

    default_value: str = '-'
    date_format: str = 'd.m.Y'
    time_format: str = 'H:i'
    date_time_format: str = 'd.m.Y H:i'

    flex_type = 'fieldset'
    template_name = 'flex_forms/fieldsets/generic_fieldset.html'
    context_object_name = 'fieldset'

    def _prepare_expressions(self, expression: str) -> str:
        # remove method's parentheses.
        # it's ok to use parentheses to indicate methods.
        return expression.replace('()', '')

    def get_data(self, instance: ModelType, field_name: str) -> tuple:
        expression = self._prepare_expressions(field_name)
        last_instance, expression_part = safety_get_attribute(instance, expression, get_last_object=True,
                                                              raise_exc=True)
        field = last_instance._meta.get_field(expression_part)
        value = self.get_field_display_value(last_instance, field)
        return last_instance, field, value

    def get_field_display_value(self, instance: ModelType, field: ModelFieldType) -> str:
        # check field type and get the value.
        method_name = 'get_%s_display'
        internal_type = field.get_internal_type()
        field_value = getattr(instance, field.name, None)
        return getattr(self, method_name % camel_to_snake(internal_type),
                       self.get_default_display)(field, field_value) or self.default_value

    def get_default_display(self, field: ModelFieldType, field_value: Any) -> str:
        display_value = None
        if field_value and getattr(field, 'choices'):
            display_value = self.get_choice_field_display(field, field_value)
        elif field_value:
            display_value = str(field_value)

        return display_value

    def get_foreign_key_display(self, field: ModelFieldType, field_value: Any) -> str:
        return str(field_value) if field_value else None

    def get_many_to_many_field_display(self, field: ModelFieldType, field_value: Any) -> str:
        return ', '.join([str(related) for related in field_value.iterator()])

    def get_time_field_display(self, field: ModelFieldType, field_value: Any) -> str:
        return format_date(field_value, self.time_format)

    def get_date_field_display(self, field: ModelFieldType, field_value: Any) -> str:
        return format_date(field_value, self.date_format)

    def get_date_time_field_display(self, field: ModelFieldType, field_value: Any) -> str:
        return format_date(field_value, self.date_time_format)

    def get_choice_field_display(self, field: ModelFieldType, field_value: Any) -> str:
        display_value = self.default_value
        if field_value:
            choices = dict(field.choices)
            if isinstance(field_value, (int, str, bool)):
                display_value = choices.get(field_value, field_value)
            elif isinstance(field_value, list):  # ArrayField
                display_value = ', '.join([str(choices.get(value_item, value_item)) for value_item in field_value])

        return display_value


class StaticModelFieldsetMixin(StaticFieldsetMixin):

    labels: dict = {}

    def __init__(self, instance, *args, **kwargs):
        self.instance = instance
        super().__init__(*args, **kwargs)
        self.prepare_static_fieldset()
        self._update_static_fields()

    def prepare_static_fieldset(self) -> None:
        pass

    def _update_static_fields(self):
        collector = Collector()
        static_fields = collector.get_all_nodes_from_dict(self.get_grid())
        for field_name in static_fields:
            if field_name not in self.static_class_fields and field_name not in self.static_fieldset:
                last_instance, field, value = self.get_data(self.instance, field_name)
                field_verbose_name = getattr(field, 'verbose_name', '').capitalize()
                verbose_name = self.labels.get(field_name) or field_verbose_name
                self.static_fieldset.update({field_name: StaticFlexField(data=value, label=verbose_name)})


class FlexFormMixMixin(FieldWrapperMixin, StaticFieldsSupportMixin):
    """
    Allows render mixed groups of flex objects - forms / model forms / formsets.
    """

    flex_type = 'flex_group'
    template_name = 'flex_forms/forms/group_template.html'
    context_object_name = 'group'
    html_params = {'method': 'POST', 'action': '/'}

    def __init__(self, form_objects, *args, **kwargs):
        self.form_objects = form_objects
        self.fields = OrderedDict()
        self.forms = []
        self.bound_fields = OrderedDict()
        super().__init__(*args, **kwargs)
        self._collect_fields(form_objects)

    def _update_fields(self, form_object: Any) -> None:
        # get bound fields from the form.
        form_fields = getattr(form_object, 'fields', None)
        if form_fields:
            self.fields.update(form_object.fields)
            prefix = form_object.prefix
            self.bound_fields.update({
                f'{prefix + "-" if prefix else ""}{field_name}': form_object[field_name]
                for field_name in form_object.fields.keys()
            })
        self.static_fieldset.update(form_object.static_fieldset)

    def _collect_fields(self, form_objects: Iterable) -> None:
        for item in form_objects:
            if isinstance(item, BaseForm):
                self._update_fields(item)
                self.forms.append(item)
            elif isinstance(item, BaseFormSet):
                self._collect_fields(item)

    def __getitem__(self, name):
        return self.bound_fields[name]

    def __iter__(self):
        for item in self.form_objects:
            yield item


class FlexFormErrorsMixin:
    """
    Adds a static field to the form with array of collected form errors.
    """

    form_errors_field_name: str = 'form_errors'

    def full_clean(self):
        super().full_clean()
        self.set_form_errors_to_field()

    def set_form_errors_to_field(self) -> None:
        form_errors = self.get_form_errors()
        form_field = self.get_form_errors_static_field()
        for error in form_errors:
            form_field.add_data(self.get_form_error_element(error))

    def get_form_errors(self) -> Iterable:
        form_errors = []
        if hasattr(self, 'non_field_errors'):
            form_errors = self.non_field_errors()
        return form_errors

    def get_form_errors_static_field(self) -> FlexDataArrayType:
        return self.static_fieldset[self.form_errors_field_name]

    def get_form_error_element(self, data: Any) -> FormErrorType:
        return FormError(data)

# endregion


# region Meta classes


class StaticFlexFieldsMetaclass(type):
    """
    Metaclass for collecting StaticFlexField fields from parent classes and assigning them to
    static_fields class variable.
    """

    def __new__(mcs, name, bases, attrs):
        static_fields = []
        for key, value in list(attrs.items()):
            if isinstance(value, BaseStaticFlexField):
                static_fields.append((key, value))
                attrs.pop(key)
        attrs['static_fields'] = OrderedDict(static_fields)

        new_class = super().__new__(mcs, name, bases, attrs)

        # Walk through the MRO.
        static_fields = OrderedDict()
        for base in reversed(new_class.__mro__):
            # Collect fields from base class.
            if hasattr(base, 'static_fields'):
                static_fields.update(base.static_fields)
            # Field shadowing.
            for attr, value in base.__dict__.items():
                if value is None and attr in static_fields:
                    static_fields.pop(attr)

        new_class.static_class_fields = static_fields

        return new_class


class FlexFormObjectMetaclass(StaticFlexFieldsMetaclass, DeclarativeFieldsMetaclass):
    """
    Provides static fields collect from mro.
    """

    pass


class FlexModelFormMetaclass(StaticFlexFieldsMetaclass, ModelFormMetaclass):
    """
    A metaclass, such as for FlexForm, but a subclass of ModelFormMetaclass.
    """

    pass


# endregion


# region Main classes


class StaticFieldset(StaticFieldsetMixin, metaclass=StaticFlexFieldsMetaclass):
    """
    Class for render static fieldsets. Not a classic form. Only StaticFlexField field class is allowed.
    """

    pass


class StaticModelFieldset(StaticModelFieldsetMixin, metaclass=FlexFormObjectMetaclass):
    """
    Class for rendering static model fieldsets.
    """

    pass


class FlexFormMix(FlexFormMixMixin, metaclass=StaticFlexFieldsMetaclass):
    pass


class FlexForm(FlexFormMixin, Form, metaclass=FlexFormObjectMetaclass):
    pass


class FlexModelForm(FlexFormMixin, ModelFormMethods, ModelForm, metaclass=FlexModelFormMetaclass):
    pass


class FlexFormset(FlexFormsetMixin, BaseFormSet):
    pass


class FlexModelFormset(FlexFormsetMixin, BaseModelFormSet):
    pass


class FlexInlineFormset(FlexFormsetMixin, BaseInlineFormSet):
    pass

# endregion
