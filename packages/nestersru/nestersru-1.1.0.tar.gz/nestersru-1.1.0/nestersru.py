"""This is nester.py module. This module has the iter() function. This function is used for iterating through the lists."""
# iter(l) function takes one list parameter. It prints out each element from the provided list, even if the list has multiple nested lists.


def iter(l, level):
# Second argument is for providing the number of tab stops while printing the nested list
	for e in l:
		if isinstance(e,  list):
			iter(e, level+1)
		else:
			for tabstop in range(level):
				print("\t", end = ' ')
				print(e)