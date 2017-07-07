import itertools
import copy

my_list = ["1", "a", [1, 2, 3], "hello", ["c", "d"], "lol"]
list_idx = [2, 4]
list_flags = [False, False, True, False, True, False]



def augment_data(my_list, list_idx):
    list_of_lists = [my_list[idx] for idx in list_idx]
    combinations = itertools.product(*list_of_lists)
    new_data = []
    for item in combinations:
        for iii, idx in enumerate(list_idx):
            entry = my_list
            entry[idx] = item[iii]
        new_data.append(copy.deepcopy(entry))
        print entry
    return(new_data)

augment_data(my_list, list_idx)