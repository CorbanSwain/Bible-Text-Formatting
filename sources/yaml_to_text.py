#!python3
# yaml_to_text.py

import c_swain_python_utils as csutils
import argparse
import os
import glob
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

L = None


class FindChangeParams:
    def __init__(self,
                 fctype=None,
                 name=None,
                 find=None,
                 change=None,
                 options=None,
                 repeat=None):

        self.type = fctype
        self.find_settings = find
        self.name = name
        self.change_settings = change
        self.options = options
        self.repeat = repeat

    @property
    def find_settings_jstr(self):
        return dict_to_jstr(self.find_settings)

    @property
    def change_settings_jstr(self):
        return dict_to_jstr(self.change_settings)

    @property
    def options_jstr(self):
        return dict_to_jstr(self.options)

    def _command_list_line(self, name_tag=''):
        line = '\t'.join([self.type,
                          self.find_settings_jstr,
                          self.change_settings_jstr,
                          self.options_jstr,
                          self.name + name_tag])
        return line

    def command_list_lines(self, line_end='\n'):
        if self.repeat is None:
            return [self._command_list_line() + line_end]
        else:
            return [self._command_list_line(name_tag=f' [repeat {i+1:d}]')
                    + line_end for i in range(self.repeat)]


def dict_to_jstr(d):
    out_strs = []
    for k, v in d.items():
        assert type(k) is str, f'Key must be a string, got {type(k)}'

        typ = type(v)
        if typ is int:
            out_strs.append(f'{k}:{v:d}')
        elif typ is float:
            out_strs.append(f'{k}:{v:f}')
        elif typ is bool:
            out_strs.append(f'{k}:{("true" if v else "false"):s}')
        elif type(v) is str:
            if v.startswith('`'):
                assert v.endswith('`'), 'Expected ` at end of string.'
                out_strs.append(f'{k}:{v[1:-1]}')
            else:

                v_escaped = v.replace('\\', '\\\\')
                v_escaped = v_escaped.replace('"', '\\"')
                out_strs.append(f'{k}:"{v_escaped}"')
        else:
            raise ValueError(f'Unexpected type of dict value found, {typ}.')

    return f'{{ {", ".join(out_strs)} }}'


def yaml_to_findchange_list(yaml_path):
    yaml_data = csutils.read_yaml(yaml_path)

    DEFAULT_KEY = '_DEFAULT_'
    FIND_KEY = 'find'
    CHANGE_KEY = 'change'
    OPTIONS_KEY = 'options'
    REPEAT_KEY = 'repeat'
    TYPE_KEY = 'type'

    try:
        default_dict = yaml_data[DEFAULT_KEY]
        del yaml_data[DEFAULT_KEY]
    except KeyError:
        default_dict = dict()

    default_find_settings = (default_dict[FIND_KEY]
                             if FIND_KEY in default_dict else dict())
    default_change_settings = (default_dict[CHANGE_KEY]
                               if CHANGE_KEY in default_dict else dict())
    default_options = (default_dict[OPTIONS_KEY]
                       if OPTIONS_KEY in default_dict else dict())
    default_type = (default_dict[TYPE_KEY]
                    if TYPE_KEY in default_dict else None)
    default_repeat = (default_dict[REPEAT_KEY]
                      if REPEAT_KEY in default_dict else None)

    output = []
    for k, v in yaml_data.items():
        name = k

        _type = v[TYPE_KEY] if TYPE_KEY in v else default_type

        findset = v[FIND_KEY] if FIND_KEY in v else dict()
        [findset.setdefault(kk, vv)
         for kk, vv in default_find_settings.items()]

        changeset = v[CHANGE_KEY] if CHANGE_KEY in v else dict()
        [changeset.setdefault(kk, vv)
         for kk, vv in default_change_settings.items()]

        options = v[OPTIONS_KEY] if OPTIONS_KEY in v else dict()
        [options.setdefault(kk, vv)
         for kk, vv in default_options.items()]

        repeat = v[REPEAT_KEY] if REPEAT_KEY in v else default_repeat

        fcp = FindChangeParams(name=name,
                               fctype=_type,
                               find=findset,
                               change=changeset,
                               options=options,
                               repeat=repeat)
        output += fcp.command_list_lines()

    return output


def convert_file(file_path, debug_mode=False):
    (file_dir, file_name) = os.path.split(file_path)

    L.info(f'Performing conversion of "{file_name}".')

    output_name = file_name.split('.')
    output_name = '.'.join(output_name[:-1] + ['tsv'])
    out_file = os.path.join(file_dir, output_name)

    try:
        lines = yaml_to_findchange_list(file_path)
        L.info('> Yaml conversion succeeded.')
    except Exception as e:
        L.warning(f'> Yaml conversion failed with error: '
                  f'{e.__class__.__name__} | "{e}".')
        if debug_mode:
            raise e
        else:
            return

    L.info(f'> Writing {len(lines)} output commmands to "{output_name}".')

    with open(out_file, 'w') as f:
        f.writelines(lines)

    print('')


def convert_all_files(conversion_dir, **kwargs):
    found_files = glob.glob(os.path.join(
        conversion_dir, '**', '*.yaml'), recursive=True)

    L.info(f'Found {len(found_files):d} .yaml file(s) for conversion.')

    for found_file in found_files:
        convert_file(found_file, **kwargs)


class YamlConversionEventHandler(FileSystemEventHandler):
    def __init__(self, search_dir):
        self.search_dir = search_dir
        self.ignore_ext = False

    def on_any_event(self, event):
        if event.is_directory:
            convert_all_files(self.search_dir)
        else:
            src_path = event.src_path
            if src_path.endswith('.yaml') or self.ignore_ext:
                convert_file(event.src_path)


def main():
    parser = argparse.ArgumentParser(description='yaml to find-change list '
                                                 'conversion')
    parser.add_argument('search_path',
                        metavar='search-path',
                        default=None,
                        nargs='?',
                        help='yaml file path or a directory containing yaml '
                             'files, can be nested. '
                             '(default is "text_find_change_descrip" dir)')
    parser.add_argument('-w', '--watch',
                        action='store_true',
                        dest='do_watch',
                        help='flag to monitor `search-path` for changes '
                             'indefinently')
    args = parser.parse_args()

    global L
    L = csutils.get_logger('yaml_to_text')

    L.info('Beginning conversion script.')
    if args.search_path is None:
        search_path = os.path.join(csutils.get_filepath(__file__),
                                   '..', 'text_find_change_descrip')
    else:
        search_path = args.search_path

    if os.path.isdir(search_path):
        convert_all_files(search_path)
        did_pass_dir = True
    else:
        convert_file(search_path)
        did_pass_dir = False

    if not args.do_watch:
        return

    event_handler = YamlConversionEventHandler(search_path)
    event_handler.ignore_ext = not did_pass_dir
    observer = Observer()
    observer.schedule(event_handler, search_path, recursive=did_pass_dir)
    observer.start()

    L.info('Monitoring directory for changes ...')
    try:
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()

