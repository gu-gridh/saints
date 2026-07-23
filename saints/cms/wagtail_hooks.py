from wagtail import hooks
from wagtail.admin.rich_text.editors.draftail import features as draftail_features
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler


@hooks.register("register_rich_text_features")
def register_arrow_link_feature(features):
    feature_name = "arrow-link"
    type_ = "ARROW_LINK"
    tag = 'span class="richtext-arrow-link"'

    control = {
        "type": type_,
        "label": "→",
        "description": "Arrow link",
        "style": {
            "border": "1px solid currentColor",
            "borderRadius": "999px",
            "padding": "0 4px",
        },
    }

    features.register_editor_plugin(
        "draftail",
        feature_name,
        draftail_features.InlineStyleFeature(control),
    )

    features.register_converter_rule("contentstate", feature_name, {
        "from_database_format": {
            'span[class="richtext-arrow-link"]': InlineStyleElementHandler(type_),
        },
        "to_database_format": {
            "style_map": {
                type_: tag,
            },
        },
    })

    features.default_features.append(feature_name)
