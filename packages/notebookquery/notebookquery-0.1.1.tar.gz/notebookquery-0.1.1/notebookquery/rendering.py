from copy import deepcopy

import nouns
import results
from IPython.core.display import HTML, display

x = nouns.get_x()
t = nouns.Templates(folders=[nouns.BUILTIN_TEMPLATES_FOLDER], preprocess=x)


def get_css():
    css = results.resource_text("css/custom.css")
    return f"<style>{css}</style>"


def load_css(css):
    display(HTML(css))


def render(data):
    return t.render(deepcopy(data))


def results_object_repr_html(self):
    return render(self)


results.Results._repr_html_ = results_object_repr_html
