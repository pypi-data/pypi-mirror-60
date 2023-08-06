def print_lol(the_lists):
    for each_list in the_lists:
        if(isinstance(each_list, list)):
            print_lol(each_list)
        else:
            print(each_list)

