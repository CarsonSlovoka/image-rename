"""
http://localhost:8000/
python -m http.server
"""

import pygments.styles
from pathlib import Path
from datetime import datetime
from typing import List
import types
from docutils.writers._html_base import HTMLTranslator


if 'sys path setting':
    import sys
    import os

    sys.path.append(str(Path(__file__).parent))  # _static/uml/...
    plantuml = f'java -jar {Path(os.environ["USERPROFILE"]) / Path("plantuml.jar")}'  # download: https://plantuml.com/en/download

    sys.path.append(str(Path(__file__).parent.parent))  # __version__ # use for ``.. automodule``
    from grid_extractor import __version__

master_file = Path(__file__).parent / Path('index.rst')
source_dir = Path(__file__).parent
output_path = None  # default Path(master_file).parent.parent / docs / language

master_doc = master_file.stem
project = 'Image Rename'  # project_name
pypi_project_name = 'image-rename'
release = __version__  # full_version: x.x.x
version = __version__[:__version__.rfind('.')]  # short_version: x.x
copyright = f'2020-{datetime.now().year} Carson'
author = 'Carson Tseng'
language = 'en'  # 'zh_TW' # https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-language  # docutils.languages/*.py

# source_encoding = 'utf-8-sig' default
source_suffix = ['.rst', '.md']
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.mathjax',
    'sphinxcontrib.plantuml',
    '_ext.txtlexer',
    '_ext.select_language',
    '_ext.plugin_disqus',
    '_ext.plugin_extra_html',
    '_ext.rst_roles',
]

todo_include_todos = True
pygments_style = pygments.styles.STYLE_MAP['vim'].split('::')[0]  # https://help.farbox.com/pygments.html  # https://pygments.org/demo/

exclude_patterns = [  # A list of glob-style patterns that should be excluded when looking for source files.

]

with open(Path(__file__).parent / Path('_static/css/user.define.rst'), 'r') as f:
    # If your style is not working, try to set FORCE_REBUILD to True.
    user_define_role = f.read()

# will be included at the end of every source file that is read.

rst_epilog = '\n'.join([
    user_define_role + '\n',  # it needs double \n
])

#  will be included at the beginning of every source file that is read.
rst_prolog = '\n'.join([
])


if 'html setting':
    html_static_path = ['_static', ]  # search ``def copy_html_static_files``

    html_extra_path = [  # Put these HTML to the root of output_dir, but it will not allow you use other variable by default.
    ]
    html_css_files = ['css/user_define.css',  # copy_asset(src=Path(self.confdir)/entry), out=Path(self.outdir) / Path('_static'))
                      'css/pygments.vim.css',
                      'css/themes/rtd.page.css',
                      'css/select.css',
                      'css/toggle_btn.css',
                      ]
    html_js_files = [  # search ``def setup_js_tag_helper``
        'js/select.js',
        'js/navbar.js',
    ]

    html_show_sourcelink = False
    html_copy_source = False

    html_show_sphinx = False
    templates_path = ['_templates/sphinx_rtd_theme'
                      ]  # A list of paths that contain extra templates (or **overwrite**). The path of content, which is Relative paths are taken as relative to the configuration directory.
    if 'my setting':
        extra_html_path = ['disqus_statistic.html', ]
        for extra_html in extra_html_path:
            assert (Path(__file__).parent / Path(templates_path[0]) / Path(extra_html)).exists(), FileNotFoundError(extra_html)
    # html_theme_path = ["_templates"]  # from ``Lib\site-packages\{theme}\`` copy to ``.\_templates/{theme}``  and **theme.conf** must exist!
    html_theme = 'sphinx_rtd_theme'  # 'nature'
    html_theme_options = {  # see Lib\site-packages\{theme}\theme.conf
        # "analytics_id": "",
        'style_external_links': True,  # Add an icon next to external links.
        "style_nav_header_background": "#4e917a",
        # 'analytics_id': 'UA-????????-?'
    }

    html_context = {
        "display_github": True,  # see the breadcrumbs.html
        'github_user': 'CarsonSlovoka',
        'github_repo': pypi_project_name,
        'github_version': 'master/',
        'conf_py_path': "doc/",

        # other setting
        # "last_updated": True,  # Copyright ... Last updated on True.
    }
    html_favicon = '_static/tab.favicon.png'  # Modern browsers use this as the **icon for tabs**.
    html_logo = '_static/nav_bar.logo.png'  # An image file that is the logo of the docs. It is placed at the top of the **sidebar**
    # html_search_language = 'zh'  # language[:2]  # https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_search_language

if 'localization':
    locale_dirs = ['locale/']  # path is example but recommended.

    if 'my setting':
        support_lang_list = [('en', ""), ('zh_TW', '繁體中文 待開發'), ]
        get_text_output_dir = Path(__file__).parent / '_gettext'

if 'my setting':
    # LEXERS = dict()  # https://stackoverflow.com/questions/16469869/custom-syntax-highlighting-with-sphinx
    NO_JEKYLL = True  # you need to create an empty file in the root directory that lets GitHub know you aren't using Jekyll to structure your site.

    write_all_output_file = False  # write all files (default: only write new and changed files)  # -a https://www.sphinx-doc.org/en/1.2/invocation.html#cmdoption-sphinx-build-a
    refresh_env = False  # set True if you want to rebuild.  # -D  https://www.sphinx-doc.org/en/1.2/invocation.html#cmdoption-sphinx-build-E

    if 'Disqus':
        disqus_short_name = pypi_project_name
        disqus_url_root = f'https://carsonslovoka.github.io/{disqus_short_name}/{language}'
