"""test test test test"""
def print_lol1778 (the_list):
	for item in the_list:
		if isinstance(item, list):
			print_lol(item)
		else:
			print(item)
