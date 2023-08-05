
# -------- Web site content etc --------------------
# These aren't currently used ... just a placeholder
# in case it seems wise to have some content/style
# stuff somewhere independent of a particular application.
#
# If used in an actual Flask application you'll need to
# use flask.render_template_string( ) instead of render_template

import pkg_resources
from . import static
from . import templates

def threeza_template(page_name:str)->str:
    filepath = pkg_resources.resource_filename("threeza", "templates/"+page_name)
    with open(filepath) as f:
        html = f.read()
    return html

def threeza_static(page_name:str)->str:
    filepath = pkg_resources.resource_filename("threeza", "static/"+page_name)
    with open(filepath) as f:
        text = f.read()
    return text
