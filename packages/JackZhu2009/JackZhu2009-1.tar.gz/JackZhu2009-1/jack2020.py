"""This is the "jack2020.py" module and it provides one function called print_101() which prints lists that may or may not include nested lists.""" 
def print_101(the_list,indent=False,level=0)
    for each_item in the_list:
        if isinstance(each_item,list):
            print_101(each_item,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end='')
            print(each_item)
		
