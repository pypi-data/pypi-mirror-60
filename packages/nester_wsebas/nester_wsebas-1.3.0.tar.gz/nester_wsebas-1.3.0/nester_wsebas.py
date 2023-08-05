def print_lol(the_list, indent = False, level = 0):
#If one of the elements of the list is a nested list, 
#this for loop prints all elements of the nested list, recursively.
#It also indents one tab for every nested list"""

	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item, indent, level + 1)
		else:		
			#if indent: checks if indent is true
			if indent:
				for tab_stop in range(level):
					print("\t", end='')
				#Instead of the for loop, you can use: 
				#print("\t" * level, end='')
			print(each_item)
