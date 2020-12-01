from io import StringIO, BytesIO
from lxml import etree
from collections import defaultdict
import src.data
import urllib

def processSchema(element, params):

    # output contains the ttl output
    if 'output' not in params.keys():
        params['output'] = StringIO()
    if 'log' not in params.keys():
        params['log'] = StringIO()
    
    ns = params['namespaces']

    base = params['base']
    base = base.replace("eu/eu", "eu") # strange difference between actual location and uri
    base = base.replace("nl/fr/", "") # strange difference between actual location and uri
    params['abs_base'] = params['base']
    for key in ns:
        if base.lower() == ns[key].lower():
            base = key
    params['base'] = base
 
    params['log'].write("processing schema   "+base+"\n")

    targetNs = element.attrib.get("targetNamespace")

    if targetNs in ["http://www.xbrl.org/2003/instance",
                    "http://xbrl.org/2005/xbrldt",
                    "http://www.xbrl.org/2003/XLink", 
                    "http://xbrl.org/2008/variable",
                    "http://www.xbrl.org/2003/linkbase"]:
        return params
    else:
        processElements(element, base, targetNs, params)

    return params

def processElements(node, base, targetNs, params):

    output = params['output']
    base = params['base']
    ns = params['namespaces']

    header_printed = False

    for child in node:

        if header_printed == False:
            output.write("\n# CONCEPTS\n")
            output.write("# localname: "+str(etree.QName(node.tag).localname)+"\n")
            output.write("# base: "+str(base)+"\n\n")
            header_printed = True

        if (child.tag == '{http://www.w3.org/2001/XMLSchema}element'):

            child_name = child.attrib.get('name', None)
            child_id = child.attrib.get('id', None)
            child_type = child.attrib.get('type', None)
            child_periodType = child.attrib.get('{http://www.xbrl.org/2003/instance}periodType', None)
            child_balance = child.attrib.get('balance', None)

            output.write(turtlename(base, child_name, ns)+"\n")

            if child_type is not None:
                output.write("    rdf:type "+child_type+" ;\n")

            if child_id is not None:
                output.write('    rdf:id "'+child_id+'" ;\n')

            if child_periodType is not None:
                output.write('    xbrli:periodType "'+child_periodType+'" ;\n')

            output.write('    .\n')
            # if child_balance is not None:
            #     output.write(';\n    xbrli:balance "'+child_balance+ '"')

    return params

def turtlename(base, name, ns):

    if 'http' in base:
        return '<'+base+":"+name+">"
    else:
        return base+":"+name
