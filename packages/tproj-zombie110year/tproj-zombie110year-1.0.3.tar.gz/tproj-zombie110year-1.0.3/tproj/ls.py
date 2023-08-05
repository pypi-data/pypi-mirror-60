from pathlib import Path
from typing import List
from zipfile import ZipFile

import yaml

from .utils import get_templates


def ls_main():
    """列出所有可用的模板归档"""
    paths = get_templates()
    filenames = [i.stem for i in paths]
    descriptions = [get_description(i) for i in paths]
    maxlen = max((len(i) for i in filenames))
    templates = f"{{fn:>{maxlen}}} |{{desc}}"
    for fn, desc in zip(filenames, descriptions):
        maxlen2 = 80 - maxlen
        if len(desc) < maxlen2:
            print(templates.format(fn=fn, desc=desc))
        else:
            print(templates.format(fn=fn, desc=desc[:maxlen2-3] + "..."))


def get_description(path: Path) -> str:
    zf = ZipFile(path)
    try:
        cfg_file = zf.open("tproj.yaml")
        cfg = yaml.load(cfg_file, Loader=yaml.BaseLoader)
        description = cfg.get("description", "")
    except KeyError as e:
        print(f"{path} don't have tproj.yaml file")
        description = ""
    return description
