from pygments.lexers import get_lexer_by_name  # refer LEXERS
from pygments.lexers._mapping import LEXERS
from pygments.lexers.data import JsonLexer
from pygments.lexers.python import PythonLexer


def setup(app):
    """
    Change txt to Python style.

    .. code-block:: txt

        ...
    """
    # app.add_lexer('txt', get_lexer_by_name('py'))
    app.add_lexer('txt', PythonLexer)
