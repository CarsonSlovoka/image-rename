from docutils.parsers.rst import roles
from docutils import nodes
from docutils.parsers.rst.states import Inliner
import docutils.parsers.rst.roles


def strike_role(role, rawtext, text, lineno, inliner: Inliner, options={}, content=[]):
    """

    USAGE: :del:`your context`

    :param role: my-strike
    :param rawtext:  :my-strike:`your context`
    :param text: your context
    :param lineno:
    :param inliner:
    :param options:
    :param content:
    :return:
    """

    # roles.set_classes(options)
    # options.setdefault('classes', []).append("mys")
    node = nodes.inline(rawtext, text, **dict(classes=['strike']))
    return [node], []


def setup(app):
    roles.register_canonical_role('del', strike_role)
