from IPython import get_ipython

from .rendering import get_css, load_css
from .sqlext import load_ipython_extension

ipython = get_ipython()
load_ipython_extension(ipython)

css = get_css()
load_css(css)
