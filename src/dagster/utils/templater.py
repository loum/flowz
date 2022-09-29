"""Templating capability.

"""
from typing import Text
import os
import logging
import shutil
import tempfile
import jinja2


def build_from_template(env_map: dict,
                        template_file_path: Text,
                        write_output: bool =False) -> Text:
    """Take *template_file_path* and template against variables
    defined by *env_map*.

    *template_file_path* needs to end with a ``.j2`` extension as the generated
    content will be output to the *template_file_path* less the ``.j2``.

    A special custom filter ``dry_override`` is available to bypass *env_map* and
    source the environment for variable substitution.  Use the custom filter
    ``dry_override`` in your template as follows::

        "test" : {{ "default" | dry_override('CUSTOM') }}

    Provided an environment variable as been set::

        export CUSTOM=some_value

    The template will render::

        ``some_value``

    Otherwise::

        ``default``

    """
    def dry_override(value, key):
        return os.getenv(key, value)

    def env_override(value, key):
        return os.getenv(key, value)

    target_template_file_path = os.path.splitext(template_file_path)

    output = None
    try:
        file_loader = jinja2.FileSystemLoader(os.path.dirname(template_file_path))
        j2_env = jinja2.Environment(autoescape=True, loader=file_loader)

        j2_env.filters['dry_override'] = dry_override
        j2_env.filters['env_override'] = env_override
        template = j2_env.get_template(os.path.basename(template_file_path))

        output = template.render(**env_map)

        if write_output:
            with tempfile.NamedTemporaryFile() as out_fh:
                out_fh.write(output.encode())
                out_fh.flush()
                shutil.copy(out_fh.name, target_template_file_path[0])
                logging.info('Templated file "%s" generated', target_template_file_path[0])
    except jinja2.exceptions.TemplateNotFound as err:
        logging.error('Skipping templating: TemplateNotFound "%s"', err)

    return output
