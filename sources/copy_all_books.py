
import argparse
import os
import c_swain_python_utils as csutils
import shutil


_book_list = None
L = None


def load_book_list(file_name='esv_books.txt'):
    global _book_list

    if _book_list is None:
        data_dir = os.path.join(csutils.get_filepath(__file__),
                                '..',
                                'data')
        book_list_filepath = os.path.join(data_dir, file_name)
        with open(book_list_filepath, 'r') as f:
            _book_list = f.readlines()

        _book_list = [s.strip() for s in _book_list]

    return _book_list


def prepend_book_title_to_file(path_dict):
    L.info('Pre-pending book name to each file.')
    for b, pth in path_dict.items():
        with open(pth, 'r') as f:
            lines = f.readlines()

        newlines = [b + '\n', ] + lines

        with open(pth, 'w') as f:
            f.writelines(newlines)


def copy_for_all_books(file_path, tag='', overwrite=False):
    _dir, tail = os.path.split(file_path)
    split_tail = tail.split('.')
    old_name, old_ext = ('.'.join(split_tail[:-1]), split_tail[-1])
    if '.' in tag:
        split_tag = tag.split('.')
        tag_name, tag_ext = ('.'.join(split_tag[:-1]), split_tag[-1])
        new_ext = tag_ext
    else:
        tag_name = tag
        new_ext = old_ext

    new_paths = dict()

    for i, b in enumerate(load_book_list()):
        new_name = f'{i + 1:02d}_{b.replace(" ", "-"):s}{tag_name:s}.{new_ext:s}'
        new_path = os.path.join(_dir, new_name)

        if not overwrite and os.path.exists(new_path):
            L.warning(f'"{new_name:30s}" already exists, skipping.')
            continue

        new_paths[b] = new_path
        shutil.copyfile(file_path, new_path)

    L.info(f'{len(new_paths):d} of {len(load_book_list()):d} file(s) copied.')

    return new_paths


def main():
    global L
    L = csutils.get_logger('copy_all_books')

    parser = argparse.ArgumentParser(description='copy file for each book of Bible.')
    parser.add_argument('path',
                        help='path to a file which will be copied for each book of the Bible')
    parser.add_argument('--prepend-book', '-b',
                        dest='do_add_title',
                        action='store_true',
                        help='prepend the book title to the file contents '
                             '(only use with text files)')
    parser.add_argument('--tag', '-t',
                        action='store',
                        default='',
                        help='add a tag to the end of each of the document names; '
                             'file extension is maintained if a new one is not '
                             'passed in the tag')
    parser.add_argument('--overwrite', '-o',
                        action='store_true',
                        help='flag to overwrite existing files, otherwise copy will be'
                             ' skipped if file exists.')

    args = parser.parse_args()

    if os.path.isfile(args.path):
        L.info('Copying file for each book of the bible.')
        out_path_dict = copy_for_all_books(args.path,
                                           tag=args.tag,
                                           overwrite=args.overwrite)
        if args.do_add_title:
            prepend_book_title_to_file(out_path_dict)
    else:
        L.error(f'Passed file could not be found: "{args.path:s}".')


if __name__ == '__main__':
    main()
