import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from crystal_toolkit.helpers.layouts import Label
from crystal_toolkit.components.transformations.core import TransformationComponent

from pymatgen.transformations.standard_transformations import (
    AutoOxiStateDecorationTransformation,
)


class AutoOxiStateDecorationTransformationComponent(TransformationComponent):
    @property
    def title(self):
        return "Detect likely oxidation states"

    @property
    def description(self):
        return """Annotate the crystal structure with likely oxidation states 
using a bond valence approach. This transformation can fail if it cannot find 
a satisfactory combination of oxidation states, and might be slow for large 
structures. 
"""

    @property
    def transformation(self):
        return AutoOxiStateDecorationTransformation

    def options_layout(self, inital_args_kwargs):
        return html.Div()

    def generate_callbacks(self, app, cache):
        super().generate_callbacks(app, cache)

        # TODO: this is a bug, should be removed
        @app.callback(
            Output(self.id("transformation_args_kwargs"), "data"),
            [Input(self.id("doesntexist"), "value")],
        )
        def update_transformation_kwargs(*args):
            return {"args": [], "kwargs": {}}
