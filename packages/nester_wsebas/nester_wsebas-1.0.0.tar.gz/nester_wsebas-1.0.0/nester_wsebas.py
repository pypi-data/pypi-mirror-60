"""This function print_lol prints all of the elements of a list"""

def print_lol(the_list):
	
	"""If one of the elements of the list is a nested list, 
	this for loop prints all elements of the nested list, recursively"""
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)