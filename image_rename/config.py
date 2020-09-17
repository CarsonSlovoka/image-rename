from pathlib import Path

DEBUG = True
dict_hotkey = dict(
    commit=['<Return>',  # Enter
            '<space>'],
    skip=['<Tab>', '<F5>']
)
img_path_list = [f for f in Path('./test/image').glob('*') if f.suffix[1:].lower() in ('png', 'bmp', 'jpg')]
# img_path_list = [f for f in Path('./test').glob('**/*') if f.suffix[1:].lower() in ('png', 'bmp', 'jpg')]  # It's able to look the nest directory.

if DEBUG:
    print('use default config')
