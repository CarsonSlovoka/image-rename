from sphinx.application import Sphinx


def init_support_lang_list(
    app: Sphinx, pagename: str, templatename: str,
    context: dict, doctree):

    if templatename != 'page.html':
        return

    context['support_lang_list'] = app.config.support_lang_list


def setup(app: Sphinx):
    app.add_config_value('support_lang_list', default=['en', ''], rebuild='html')
    app.connect(event='html-page-context', callback=init_support_lang_list)  # https://www.sphinx-doc.org/en/master/extdev/appapi.html
