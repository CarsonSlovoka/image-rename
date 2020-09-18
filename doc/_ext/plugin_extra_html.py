__all__ = ('setup_simple_extra_html', 'setup_extra_html')

from sphinx.application import Sphinx
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util.osutil import ensuredir
from pathlib import Path
import warnings
from typing import Tuple, Union
import textwrap
import re


def expand_init_builder(app):
    Sphinx._init_builder(app)
    setup_simple_extra_html(app)
    # setup_extra_html(app)


def setup(app: Sphinx):
    app.add_config_value('extra_html_path', [], True)
    app._init_builder = lambda: expand_init_builder(app)


def check(app: Sphinx) -> Tuple[
    bool,
    Union[StandaloneHTMLBuilder, None],
    Union[dict, None]
]:
    """check builder is HTML and extra_htm_path exists"""
    if not isinstance(app.builder, StandaloneHTMLBuilder):
        return False, None, None

    if not hasattr(app.config, 'extra_html_path') or \
       not isinstance(app.config['extra_html_path'], list) or \
       len(app.config['extra_html_path']) == 0:
        warnings.warn('extra_html_path not in conf.py', UserWarning)
        return False, None, None

    html_builder = app.builder
    user_config = {attr: app.config[attr] for attr in dir(app.config) if not attr.startswith('_')}
    return True, html_builder, user_config


def collect_files(source_dir: Path, file_types: list, excludes: tuple):
    """collector the files that you write"""
    return [
        cur_file for cur_file in source_dir.glob('**/*.*')
        if (cur_file.suffix in file_types) and (cur_file.name not in excludes)
    ]


def setup_extra_html_base(app: Sphinx) -> Tuple[bool, StandaloneHTMLBuilder, dict]:
    is_ok, html_builder, user_config = check(app)
    if not is_ok:
        return False, html_builder, user_config

    list_page_name = collect_files(Path(app.srcdir), file_types=list(app.config.source_suffix), excludes=('user.define.rst', ))
    root = str(list_page_name[0].parent)+'\\'
    list_page_name = [str(_).replace(root, '') for _ in list_page_name]
    list_page_name = [_[0: _.rfind('.')] for _ in list_page_name]  # remove the suffix

    user_config = user_config.copy()
    user_config.update(dict(list_page_name=list_page_name, Path=Path))
    return True, html_builder, user_config


def setup_simple_extra_html(app: Sphinx):
    """
    if you are just want to use the variable where it exists on the config,　then you use this function is enough.
    """
    is_ok, html_builder, user_config = setup_extra_html_base(app)
    if not is_ok:
        return

    for cur_html in user_config['extra_html_path']:
        template_name = cur_html  # xxx.html
        page_name = Path(cur_html).stem  # xxx

        output_data = html_builder.templates.render(template_name, user_config)

        output_filename = html_builder.get_outfilename(page_name)
        ensuredir(Path(output_filename).parent)  # Ensure that a path exists.

        output_data = re.sub('^\n', '', textwrap.dedent(output_data), flags=re.MULTILINE)  # Search line data that contain \n begin the first character
        encoding = user_config.get('encoding', 'utf-8-sig')
        try:
            with open(output_filename, 'w', encoding=encoding, errors='xmlcharrefreplace') as f:
                f.write(output_data)
        except OSError as err:
            raise OSError(f'error writing file {page_name}. {err}')


def setup_extra_html(app: Sphinx):
    """
    if you are want to use the variable where it exists on the config, and the pathto, css_tag, hasdoc, then use this function.
    """

    is_ok, html_builder, user_config = setup_extra_html_base(app)
    if not is_ok:
        return

    html_builder.globalcontext = user_config
    # Please put your HTML to ``templates_path`` that you define, since it concept about the BuiltinTemplateLoader.pathchain
    for cur_html in user_config['extra_html_path']:
        template_name = cur_html  # xxx.html
        page_name = Path(cur_html).stem  # xxx

        html_builder.handle_page(pagename=page_name, addctx=dict(), templatename=template_name, outfilename=None)
