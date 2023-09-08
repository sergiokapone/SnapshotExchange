import docutils.core

def rst_to_html(rst_text):
    parts = docutils.core.publish_parts(
        source=rst_text,
        writer_name="html",
        settings_overrides={"initial_header_level": 2}
    )
    return parts["html_body"]