# import required modules
import numpy as np
import matplotlib.pylab as plt
import parameters
import xml.etree.cElementTree as ET

# 1st: create download url and download url from the website
def download_xml(search_url, filename):
    import parameters
    import urllib
    index = search_url.find(parameters.search_url_separating_kw)
    kw_length = len(parameters.search_url_separating_kw)
    cut_index = index + kw_length
    base_url = search_url[:cut_index]
    search_specification = search_url[cut_index:]
    search_string = base_url + parameters.download_kw + search_specification + parameters.download_specification
    response = urllib.URLopener()
    response.retrieve(search_string, filename)
    # html = response.read()
    return(filename)

xml_string = download_xml(parameters.search_url, parameters.xml_file_name)
# or directly download the xml


root = ET.fromstring(xml_string)
tree = ET.ElementTree(root)

# 2nd:



