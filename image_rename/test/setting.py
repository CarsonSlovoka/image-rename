from pathlib import Path
img_path_list = [f for f in Path('./image').glob('*') if f.suffix[1:].lower() in ('png', 'bmp', 'jpg')]
print('use test setting.py')
