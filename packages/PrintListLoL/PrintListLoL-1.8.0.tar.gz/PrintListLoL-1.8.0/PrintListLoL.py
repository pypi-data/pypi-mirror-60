"""这是我的练习模块
函数：print_lol()
作用：打印列表，其中可能包含（或不包含）嵌套列表"""
import sys
def print_lol(the_list,indent=False,level=0,fn=sys.stdout):
        """the_list 为函数的参数 ，可以是任何列表。该列表通过函数递归，每一项都输出到屏幕上，一个数据项占一行.
            第二个参数level,用来在遇到嵌套时插入制表符。"""
        for each_item in the_list:
                if isinstance(each_item,list):
                        print_lol(each_item,indent,level+1,fn)
                else:
                        if indent:
                                for tab_stop in range(level):
                                        print("\t",end='',file=fn)
                        print(each_item,file=fn)
