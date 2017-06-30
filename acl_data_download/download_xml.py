# import required modules
import parameters
import xml.etree.cElementTree as ET
import urllib2

# 1st: create download url and download url from the website
def get_xml_string(search_url):
    """
    get the search results (.xml) as a string
    :param search_url: url used for search
    :return:
    """
    index = search_url.find(parameters.search_url_separating_kw)
    kw_length = len(parameters.search_url_separating_kw)
    cut_index = index + kw_length
    base_url = search_url[:cut_index]
    search_specification = search_url[cut_index:]
    search_string = base_url + parameters.download_kw + search_specification + parameters.download_specification
    response = urllib2.urlopen(search_string)
    xml_string = response.read()
    return(xml_string)

def download_xml_file(search_url):
    """
    write the string as a .xml file
    :param search_url:
    :return:
    """
    xml_string = get_xml_string(search_url)
    with open(parameters.xml_file_name, "wb") as thefile:
        thefile.write(xml_string)
    return(None)





