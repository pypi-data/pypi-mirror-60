"""This is nester.py module. This module has the iter() function. This function is used for iterating through the lists."""
# print_nestList(l) function takes one list parameter. It prints out each element from the provided list, even if the list has multiple nested lists.


# Second argument is for providing the number of tab stops while printing the nested list.
# second argument has a default value making it as an optional argument.

def print_nestList(l, level=0):
	for i in l:
		if isinstance(i, list):
			print_nestList(i,level+1)
		else:
			for tab in range(level):
				print("\t" , end='')
			print(i)	