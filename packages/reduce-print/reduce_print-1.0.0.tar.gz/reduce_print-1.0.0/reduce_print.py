"""这是一个用于递归处理多层列表的模块     """


def print_lol(the_list):
    """print_lol函数将递归处理列表数据"""

    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print (each_item)

