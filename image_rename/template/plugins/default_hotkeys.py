from image_rename import template

register = template.Library(__name__)  # You can assign any str as a parameter. It can make the programmer easy to understand where the path of the module is.


@register.hotkey(key_list=['<F10>'])
def delete_file(widget_info: dict):
    print(widget_info.get('cur_img_path'))
    print(widget_info.get('previous_img_path'))
