# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Dashforfaceauth(Component):
    """A Dashforfaceauth component.
ExampleComponent is an example component.
It takes a property, `label`, and
displays it.
It renders an input with the property `value`
which is editable by the user.

Keyword arguments:
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- label (string; optional): label for testing
- appId (string; optional): The Identification of the APP given by Facebook for developers
- nameu (string; optional): name extracted
- n_clicks (a value equal to: 'change'; optional): property to identify when is clicked
- resultFacebookLogin (dict; optional): the outcome of the callback"""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, label=Component.UNDEFINED, appId=Component.UNDEFINED, nameu=Component.UNDEFINED, n_clicks=Component.UNDEFINED, resultFacebookLogin=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'label', 'appId', 'nameu', 'n_clicks', 'resultFacebookLogin']
        self._type = 'Dashforfaceauth'
        self._namespace = 'dashforfaceauth'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'label', 'appId', 'nameu', 'n_clicks', 'resultFacebookLogin']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Dashforfaceauth, self).__init__(**args)
