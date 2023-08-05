import _plotly_utils.basevalidators


class TextfontValidator(_plotly_utils.basevalidators.CompoundValidator):
    def __init__(
        self, plotly_name="textfont", parent_name="barpolar.selected", **kwargs
    ):
        super(TextfontValidator, self).__init__(
            plotly_name=plotly_name,
            parent_name=parent_name,
            data_class_str=kwargs.pop("data_class_str", "Textfont"),
            data_docs=kwargs.pop(
                "data_docs",
                """
            color
                Sets the text font color of selected points.
""",
            ),
            **kwargs
        )


import _plotly_utils.basevalidators


class MarkerValidator(_plotly_utils.basevalidators.CompoundValidator):
    def __init__(self, plotly_name="marker", parent_name="barpolar.selected", **kwargs):
        super(MarkerValidator, self).__init__(
            plotly_name=plotly_name,
            parent_name=parent_name,
            data_class_str=kwargs.pop("data_class_str", "Marker"),
            data_docs=kwargs.pop(
                "data_docs",
                """
            color
                Sets the marker color of selected points.
            opacity
                Sets the marker opacity of selected points.
""",
            ),
            **kwargs
        )
