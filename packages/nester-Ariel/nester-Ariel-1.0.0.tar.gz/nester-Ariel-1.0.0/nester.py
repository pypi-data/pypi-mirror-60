movies = ['A',1978,'B',1221,['Q','W','E',['S','d','A']]]
def print_lol(the_list):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)
print_lol(movies)
