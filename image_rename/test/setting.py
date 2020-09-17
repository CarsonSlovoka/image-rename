from pathlib import Path
dict_hotkey = dict(
    commit=['<Return>',  # Enter
            '<space>'],
    skip=['<Tab>', '<F5>']
)
img_path_list = [f for f in Path('./image').glob('*') if f.suffix[1:].lower() in ('png', 'bmp', 'jpg')]
print('use test setting.py')
