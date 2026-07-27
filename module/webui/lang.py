from typing import Dict

from module.config.deep import deep_iter
from module.config.utils import filepath_i18n, read_file
from module.submodule.utils import list_mod_dir
from module.webui.setting import State

LANG = "en-US"
TRANSLATE_MODE = False


def set_language(s: str, refresh=False):
    global LANG
    LANG = "en-US"
    State.deploy_config.Language = LANG
    if refresh:
        from pywebio.session import run_js
        run_js("location.reload();")


def t(s, *args, **kwargs):
    if TRANSLATE_MODE:
        return s
    return _t(s).format(*args, **kwargs)


def _t(s, lang=None):
    try:
        return dic_lang["en-US"][s]
    except KeyError:
        print(f"Language key ({s}) not found")
        return s


dic_lang: Dict[str, Dict[str, str]] = {"en-US": {}}


def reload():
    dic_lang["en-US"].clear()
    for mod_name, _ in list_mod_dir():
        for path, value in deep_iter(read_file(filepath_i18n("en-US", mod_name)), depth=3):
            dic_lang["en-US"][".".join(path)] = value
    for path, value in deep_iter(read_file(filepath_i18n("en-US")), depth=3):
        dic_lang["en-US"][".".join(path)] = value
