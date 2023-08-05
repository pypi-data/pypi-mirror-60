#This function print_lol prints all of the elements of a list
def print_lol(the_list, level):

	#If one of the elements of the list is a nested list, 
	#this for loop prints all elements of the nested list, recursively.
	#It also indents one tab for every nested list"""
	
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item, level + 1)
		else:
			for tab_stop in range(level):
				print("\t", end='')
			print(each_item)