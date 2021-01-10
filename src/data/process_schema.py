from io import StringIO, BytesIO
from lxml import etree
from collections import defaultdict
import src.data
import urllib

def processSchema(element, params):

    # output contains the ttl output
    if 'output' not in params.keys():
        params['output'] = StringIO()

    # log is for info, warnings and errors
    if 'log' not in params.keys():
        params['log'] = StringIO()
    params['log'].write("processing schema   "+base+"\n")
    
    ns = params['namespaces']

    base = params['base']
    base = base.replace("eu/eu", "eu") # strange difference between actual location and uri
    base = base.replace("nl/fr/", "") # strange difference between actual location and uri

    params['abs_base'] = params['base']
    for key in ns:
        if base.lower() == ns[key].lower():
            base = key
    params['base'] = base
 
    targetNs = element.attrib.get("targetNamespace")
    if targetNs not in ["http://www.xbrl.org/2003/instance",
                        "http://xbrl.org/2005/xbrldt",
                        "http://www.xbrl.org/2003/XLink", 
                        "http://xbrl.org/2008/variable",
                        "http://www.xbrl.org/2003/linkbase"]:
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

        if child.tag=='{http://www.w3.org/2001/XMLSchema}element':

            child_name = child.attrib.get('name', None)
            output.write(turtlename(base, child_name, ns).lower()+"\n")

            child_type = child.attrib.get('type', None)
            if child_type is not None:
                if child_type in ['string', 'anyType', 'anyURI', 'xhtml.html.type',
                                  'listener.type', 'action.type', 'script.type',
                                  'dispatchEvent.type', 'addEventListener.type',
                                  'removeEventListener.type', 'stopPropagation.type']:
                    child_type = "xbrll:"+ child_type

                output.write("    rdf:type "+child_type+" ;\n")

            child_id = child.attrib.get('id', None)
            if child_id is not None:
                output.write('    rdf:id '+turtlename(base, child_id, ns).lower()+' ;\n')

            child_periodType = child.attrib.get('{http://www.xbrl.org/2003/instance}periodType', None)
            if child_periodType is not None:
                output.write('    xbrll:periodType "'+child_periodType+'" ;\n')

            child_balance = child.attrib.get('balance', None)
            if child_periodType is not None:
                output.write('    xbrll:Balance "'+child_balance+'" ;\n')

            output.write('    .\n')

    return params

def turtlename(base, name, ns):

    if 'http' in base:
        return '<'+base+"/"+name+">"
    else:
        return base+":"+name
