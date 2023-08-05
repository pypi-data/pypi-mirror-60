import re
import os
from emlib import lib as _lib

from .config import presetsPath


def _normalizeIncludes(includes):
    """
    * removes quotations around includes if needed
    """
    out = []
    for include in includes:
        include = include.strip()
        if not include:
            continue
        include = include.replace('"', '')
        out.append(include)
    return out


_removeExtranousCharacters = _lib.makereplacer({"[": "", "]":"", '"': '', "'": "", "{":"", "}":""})


def _parseIncludeStr(s):
    """ Remove extraneous characters, split and remove quotes """
    includes = _removeExtranousCharacters(s).split(',')
    return includes


def _parseTabledef(s):
    s = _removeExtranousCharacters(s)
    rawpairs = re.split(r",|\n", s)
    out = {}
    for rawpair in rawpairs:
        if ":" not in rawpair:
            continue
        key, value = rawpair.split(":")
        key = key.strip()
        out[key] = float(value)
    return out


_UNSET = object()


def _transferKey(source:dict, dest:dict, tag:str, callback=None, default=None):
    """ transfer the value from source to dest """
    value = source.get(tag, _UNSET)
    if value is not _UNSET:
        dest[tag] = callback(value) if callback else value
    else:
        dest[tag] = default


def loadIniPreset(path: str) -> dict:
    import configparser
    cfg = configparser.ConfigParser()
    cfg.read(path)
    preset = cfg['Preset']
    d = {}
    d['audiogen'] = preset['audiogen']
    d['name'] = preset['name']
    _transferKey(preset, d, 'init')
    _transferKey(preset, d, 'tabledef', callback=_parseTabledef)
    _transferKey(preset, d, 'includes', callback=_parseIncludeStr)
    _transferKey(preset, d, 'tableinit', callback=eval)
    _transferKey(preset, d, 'tablemap', callback=eval)
    _transferKey(preset, d, 'numouts', callback=int, default=1)
    return d


def saveIniPreset(d:dict, outpath:str) -> None:
    out = {'Preset': d}
    audiogen = d['audiogen'] 
    if not audiogen.startswith("\n"):
        out['Preset']['audiogen'] = "\n" + audiogen
    includes = d.get('includes')
    if includes:
        includestr = ", ".join(includes)
        out['Preset']['includes'] = includestr
    import configparser
    cfg = configparser.ConfigParser()
    cfg.read_dict(out)
    with open(outpath, "w") as f:
        cfg.write(f)


def iniPresetTemplateStr() -> str:
    s = \
"""
[Preset]
name = {presetName}

# optional init
init = 
    gi_sample ftgen 0, 0, 0, -1, "/path/to/sample", 0, 0, 0
    gi_empty bufnew 1024

audiogen =
    ; kdeviation is autogenerated from the tabledef
    ; kfreq, kpitch and kamp are always defined 
    kamp2, kdur gaussjitter kamp, kdeviation, 5, 0.4
    kamp2 = sc_lag(lineto:k(kamp2, kdur), kdur)
    ; the code should define a aout variable
    aout = oscili:a(kamp2, kfreq)
    
# includes and tabledef are also optional
includes = em/buf.udo, em/random.udo
tabledef = deviation: 0.3, anotherParam: 1.5
"""
    return s


def makeIniPresetTemplate(presetName:str, edit=False) -> str:
    s = iniPresetTemplateStr()
    s.format(presetName=presetName)
    outpath = os.path.join(presetsPath(), f"preset-{presetName}.ini")
    with open(outpath, "w") as f:
        f.write(s)
    if edit:
        _lib.open_with_standard_app(outpath, force_wait=True)
    return outpath
