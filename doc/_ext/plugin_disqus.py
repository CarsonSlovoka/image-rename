__all__ = ('setup',)

from sphinx.application import Sphinx


def init_support_lang_list(app: Sphinx, pagename: str, templatename: str, context: dict, doctree):
    if templatename != 'page.html':
        return

    context['disqus_short_name'] = app.config.disqus_short_name
    context['disqus_url_root'] = app.config.disqus_url_root


def setup(app: Sphinx):
    app.add_config_value('disqus_short_name', default='', rebuild='html')
    app.add_config_value('disqus_url_root', default='', rebuild='html')
    app.connect(event='html-page-context', callback=init_support_lang_list)  # https://www.sphinx-doc.org/en/master/extdev/appapi.html
