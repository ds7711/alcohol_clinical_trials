import itertools
import copy
import xml.etree.cElementTree as ET

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


xml_string = """<?xml version="1.0"?>
<data>
    <country name="Liechtenstein">
        <rank>1</rank>
        <year>2008</year>
        <gdppc>141100</gdppc>
        <neighbor name="Austria" direction="E"/>
        <neighbor name="Switzerland" direction="W"/>
    </country>
    <country name="Singapore">
        <rank>4</rank>
        <year>2011</year>
        <gdppc>59900</gdppc>
        <neighbor name="Malaysia" direction="N"/>
    </country>
    <country name="Panama">
        <rank>68</rank>
        <year>2011</year>
        <gdppc>13600</gdppc>
        <neighbor name="Costa Rica" direction="W"/>
        <neighbor name="Colombia" direction="E"/>
    </country>
</data>"""

root = ET.fromstring(xml_string)
eg_country = root.find("./country")
for neighbor in eg_country.iter("neighbor"):
    neighbor_dict = neighbor.attrib
    a, b = neighbor_dict.keys()[0], neighbor_dict.values()[0]
    print a, b

def calculator(a, b):

    def plus(a, b):
        return(a+b)

    def mul(a, b):
        return(a*b)

    return(plus(a, b) + mul(a, b))
