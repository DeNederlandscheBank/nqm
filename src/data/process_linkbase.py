from io import StringIO, BytesIO
from lxml import etree
from collections import defaultdict
import src.data
import urllib

def processLinkBase(element, params):

    # output contains the ttl output
    if 'output' not in params.keys():
        params['output'] = StringIO()
    if 'log' not in params.keys():
        params['log'] = StringIO()
    # locators is the list of locators already defined
    if 'defined_locators' not in params.keys():
        params['defined_locators'] = list()
    if 'defined_resources' not in params.keys():
        params['defined_resources'] = list()
    if 'defined_links' not in params.keys():
        params['defined_links'] = list()
    
    ns = params['namespaces']

    base = params['base']
    base = base.replace("eu/eu", "eu") # strange difference between actual location and uri
    base = base.replace("nl/fr/", "") # strange difference between actual location and uri
    params['abs_base'] = params['base']
    for key in ns:
        if base.lower() == ns[key].lower():
            base = key
    params['base'] = base
 
    params['log'].write("checking linkbase   "+base+"\n")

    for node in element:

        node_type = node.attrib.get('{http://www.w3.org/1999/xlink}type', None)
        if node_type == 'extended':
            params = checkExtendedLink(node, params)
        elif node_type == "simple":
            params = checkSimpleLink(node, params)

    params['log'].write("processing linkbase "+base+"\n")

    for node in element:

        node_type = node.attrib.get('{http://www.w3.org/1999/xlink}type', None)

        if node_type == "extended":
            params = processExtendedLink(node, params)
        elif node_type == "simple":
            params = processSimpleLink(node, params)

    return params

def checkSimpleLink(node, params):

    ns = params['namespaces']
    base = params['base']

    href = node.attrib.get('{http://www.w3.org/1999/xlink}href', None)
    if href:
        p = href.split("#")[1]

        # should we process hrefs here?

    return params

def checkExtendedLink(node, params):

    ns = params['namespaces']
    base = params['base']

    for child in node:
        child_type = child.attrib['{http://www.w3.org/1999/xlink}type']
        if child_type == "locator":
            href = child.attrib['{http://www.w3.org/1999/xlink}href']
            if (href):
                uri = href
                p = uri.split("#")[1]
            #     uri = expandRelativePath(uri, base);

            #     // if resource has relative uri then parent's namespace applies
            #     const char *lns = (ns && strncmp((char *)href, "http://", 7) ? ns : NULL);

            #     // returns false if uri has already been processed
            #     if (!prependDtsQueue(XBRL_SCHEMA, (const char *)uri, base, lns, 0))
            #         ++missingSchemas;
            #         fprintf(stderr, "found unseen2: %s\n", uri);

    return params

def processSimpleLink(node, params):

    ns = params['namespaces']
    base = params['base']

    node_role = node.attrib.get('{http://www.w3.org/1999/xlink}role', None)

    if node_role is not None:
        declareRole(role, 0)

    node_role = node.attrib.get('arcrole', None)

    if node_role is not None:
        declareRole(role, 1)

    return params

def processExtendedLink(node, params):
    
    ns = params['namespaces']
    base = params['base']

    labels_nodes = defaultdict(list)

    xlink = {'role': node.attrib.get('{http://www.w3.org/1999/xlink}role'),
             'id': node.attrib.get('{http://www.w3.org/1999/xlink}id'),
             'base': node.attrib.get('{http://www.w3.org/1999/xlink}base'),
             'locators': list(),
             'arcs': list()}

    for child in node:

        child_type = child.attrib['{http://www.w3.org/1999/xlink}type']
        if child_type == 'locator':

            for key in child.attrib:
                if key not in ['{http://www.w3.org/1999/xlink}href',
                               '{http://www.w3.org/1999/xlink}type',
                               '{http://www.w3.org/1999/xlink}role',
                               '{http://www.w3.org/1999/xlink}title',
                               '{http://www.w3.org/1999/xlink}label']:
                    print("Unknown locator attribute: " + str(key))

            locator = {'href': child.attrib.get('{http://www.w3.org/1999/xlink}href', None),
                       'role': child.attrib.get('{http://www.w3.org/1999/xlink}role', None),
                       'title': child.attrib.get('{http://www.w3.org/1999/xlink}title', None),
                       'label': child.attrib.get('{http://www.w3.org/1999/xlink}label', None)}

            xlink['locators'].append(locator)

        elif child_type == 'resource':

            for key in child.attrib:
                if key not in ['{http://www.w3.org/XML/1998/namespace}lang',
                               '{http://www.w3.org/1999/xlink}role',
                               '{http://www.w3.org/1999/xlink}title',
                               '{http://www.w3.org/1999/xlink}label',
                               '{http://www.w3.org/1999/xlink}type',
                               'name',
                               'output',
                               'fallbackValue',
                               'bindAsSequence',
                               'id',
                               'aspectModel',
                               'test',
                               'implicitFiltering',
                               'parentChildOrder',
                               'abstract',
                               'merge',
                               'select',
                               'as',
                               'variable',
                               'dimension',
                               'matchAny']:
                    print("Unknown resource attribute: " + str(key))

            resource = {'node': child,
                        'lang': child.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', None),
                        'role': child.attrib.get('{http://www.w3.org/1999/xlink}role', None),
                        'title': child.attrib.get('{http://www.w3.org/1999/xlink}title', None),
                        'label': child.attrib.get('{http://www.w3.org/1999/xlink}label', None)}

            for key in ['name', 'output', 'fallbackValue', 'bindAsSequence','id',
                        'aspectModel', 'test', 'implicitFiltering','parentChildOrder',
                        'abstract', 'merge', 'select', 'as', 'variable', 'dimension', 'matchAny']:
                value = child.attrib.get(key, None)
                if value is not None:
                    resource[key] = value

            xlink['locators'].append(resource)

        elif child_type == "arc":

            for key in child.attrib:
                if key not in ['{http://www.w3.org/1999/xlink}from',
                               '{http://www.w3.org/1999/xlink}to',
                               '{http://www.w3.org/1999/xlink}arcrole',
                               '{http://www.w3.org/1999/xlink}title',
                               '{http://www.w3.org/1999/xlink}type',
                               '{http://xbrl.org/2005/xbrldt}contextElement',
                               '{http://xbrl.org/2005/xbrldt}closed',
                               '{http://xbrl.org/2005/xbrldt}targetRole',
                               '{http://xbrl.org/2005/xbrldt}usable',
                               'order', 
                               'use', 
                               'priority', 
                               'weight',
                               'name',
                               'cover',
                               'complement',
                               'axis']:
                    print("Unknown arc attribute: " + str(key))

            arc = {'fromlabel': child.attrib.get('{http://www.w3.org/1999/xlink}from', None),
                   'tolabel': child.attrib.get('{http://www.w3.org/1999/xlink}to', None),
                   'role': child.attrib.get('{http://www.w3.org/1999/xlink}arcrole', None),
                   'type': child.attrib.get('{http://www.w3.org/1999/xlink}type', None),
                   'title': child.attrib.get('{http://www.w3.org/1999/xlink}title', None),
                   'contextElement': child.attrib.get("{http://xbrl.org/2005/xbrldt}contextElement", None),
                   'closed': child.attrib.get("{http://xbrl.org/2005/xbrldt}closed", None),
                   'usable': child.attrib.get("{http://xbrl.org/2005/xbrldt}usable", None),
                   'targetRole': child.attrib.get('{http://xbrl.org/2005/xbrldt}targetRole', None)
                   }

            for key in ['order', 'use', 'priority', 'weight', 'name', 'cover', 'complement', 'axis']:
                value = child.attrib.get(key, None)
                if value is not None:
                    arc[key] = value

            xlink['arcs'].append(arc)

        else:
            print("Unknown type")

    for locator in xlink['locators']:    # if locator is not None:
        labels_nodes[locator['label']].append(locator)

    # fix up pointers between arcs and locs
    for arc in xlink['arcs']:
        arc['fromloc'] = list()
        label = arc['fromlabel']
        if label in labels_nodes.keys():
            arc['fromloc'] = labels_nodes[label]
        arc['toloc'] = list()
        label = arc['tolabel']
        if label in labels_nodes.keys():
            arc['toloc'] = labels_nodes[label]

    # translate resources into turtle
    translateResources(node, xlink['locators'], params)

    # translate locators into turtle
    translateLocators(node, xlink['locators'], params)

    # translate xlinks into turtle
    translateXLink(node, xlink['arcs'], xlink['locators'], params)

    return params

def translateResources(node, locators, params):

    ns = params['namespaces']
    base = params['base']
    output = params['output']

    header_printed = False

    for idx, locator in enumerate(locators):

        if 'node' in locator.keys():

            label = locator['label']
            if label[-1]==".":
                label = label[0:-1]
            name = turtlename(base, label, ns)

            if name.lower() not in params['defined_resources']: # if not already defined then define

                if header_printed == False:
                    output.write("\n# RESOURCES\n")
                    output.write("# localname: "+str(etree.QName(node.tag).localname)+"\n")
                    output.write("# role: "+str(node.attrib.get('{http://www.w3.org/1999/xlink}role', None)) + "\n")
                    output.write("# base: "+str(base)+"\n\n")
                    header_printed = True

                output.write(name.lower()+"\n")

                for key in ['name', 'output', 'fallbackValue', 'bindAsSequence','id',
                            'aspectModel', 'test', 'implicitFiltering','parentChildOrder',
                            'abstract', 'merge', 'select', 'as', 'variable', 'dimension', 'matchAny']:
                    value = locator.get(key, None)
                    if value is not None:
                        output.write('    xl:'+key+' "'+value+'" ;\n')

                role = locator.get('role', None)
                if role:
                    role = shortRoleName(role, 0, params)
                    output.write("    xlink:role "+role+" ;\n")

                title = locator.get('title', None)
                if title:
                    title = shortRoleName(title, 0, params)
                    output.write("    xlink:title "+title+" ;\n")

                lang = locator.get('lang', None)
                if (lang):
                    output.write('    rdf:lang "'+lang+'" ;\n')

                count = len(locator['node'])
                if count >= 1:
                    xml = ''
                    for child in locator['node']:
                        if child.text is not None:
                            xml += str(child.text)
                    output.write('    rdf:value """'+str(xml)+'"""^^rdf:XMLLiteral ;\n    .\n')
                else:
                    content = locator['node'].text
                    lang = locator.get('lang', None)
                    if lang:
                        output.write('    rdf:value """'+str(content)+'"""@'+lang+' ;\n    .\n')
                    else:
                        output.write('    rdf:value """'+str(content)+'""" ;\n    .\n')

                params['defined_resources'].append(name.lower())

def translateLocators(node, locators, params):

    ns = params['namespaces']
    base = params['base']
    output = params['output']

    header_printed = False

    for idx, locator in enumerate(locators):

        if 'href' in locator.keys():

            label = locator['label']
            if label[-1]==".": # sometimes the label end with a dot -> delete
                label = label[0:-1]
            name = turtlename(base, label, ns)

            if name.lower() not in params['defined_locators']: # if not already defined then define

                if header_printed == False:
                    output.write("\n# LOCATORS\n")
                    output.write("# localname: "+str(etree.QName(node.tag).localname)+"\n")
                    output.write("# role: "+str(node.attrib.get('{http://www.w3.org/1999/xlink}role', None)) + "\n")
                    output.write("# base: "+str(base)+"\n\n")
                    header_printed = True

                output.write(name.lower()+"\n")
                output.write('    xl:type xbrll:locator ;\n')

                role = locator.get('role', None)
                if role is not None:
                    role = shortRoleName(role, 0, params)
                    output.write("    xl:role "+role+" ;\n")

                xlink_id = locator.get('id', None)
                if xlink_id is not None:
                    xlink_id = shortRoleName(xlink_id, 0, params)
                    output.write('    xlink:id <'+xlink_id+'> ;\n')

                xlink_base = locator.get('base', None)
                if xlink_base is not None:
                    output.write('    xlink:base <'+xlink_base+'> ;\n')

                # create absolute uri instead of relative
                href = str(urllib.parse.urljoin(params['abs_base'], locator['href']))
                output.write('    xlink:href """'+href+'"""^^rdf:XMLLiteral ;\n')

                # extract concept name and define concept
                if "#" in href:
                    short = href.split("#")[1]
                # if '_' in short:
                #     short = short.split("_")[1]
                output.write('    rdf:id '+turtlename(base, short, ns).lower()+";\n    .\n")

                params['defined_locators'].append(name.lower())

def translateXLink(node, arcs, locators, params):

    ns = params['namespaces']
    base = params['base']
    output = params['output']

    # footnoteLink has xlink:role="http://www.xbrl.org/2003/role/link"
    # which isn't really worth noting in the RDF, so suppress it here

    header_printed = False

    for arc in arcs:
        for fromloc in arc['fromloc']:
            for toloc in arc['toloc']:

                if header_printed == False:
                    output.write("\n# LINKS\n")
                    output.write("# localname: "+str(etree.QName(node.tag).localname)+"\n")
                    output.write("# role: "+str(node.attrib.get('{http://www.w3.org/1999/xlink}role', None)) + "\n")
                    output.write("# base: "+str(base)+"\n\n")
                    header_printed = True

                params['linkNumber'] += 1

                str_subject = getTurtleName(fromloc, base, ns)
                str_arcrole = shortRoleName(arc['role'], 1, params)
                str_object = getTurtleName(toloc, base, ns)

                link_def = ''

                link_def += "    xlink:role "+str(str_arcrole)+" ;\n"

                # xlink_id = toloc.get('id', None)
                # if xlink_id is not None:
                #     output.write("    xlink:id "+xlink_id+";\n")

                # type not included
                # arc_type = arc.get('type', None)
                # if arc_type:
                #     link_def += '    xl:type "'+arc_type+'" ;\n'

                arc_contextElement = arc.get('contextElement', None)
                if arc_contextElement:
                    link_def += '    xbrldt:contextElement "'+arc_contextElement+'" ;\n'

                arc_targetRole = arc.get('targetRole', None)
                if arc_targetRole:
                    link_def += '    xbrldt:targetRole "'+arc_targetRole+'" ;\n'

                arc_closed = arc.get('closed', None)
                if arc_closed:
                    link_def += '    xbrldt:closed "'+arc_closed+'" ;\n'

                arc_usable = arc.get('usable', None)
                if arc_usable:
                    link_def += '    xbrldt:usable "'+arc_usable+'" ;\n'

                arc_cover = arc.get('cover', None)
                if arc_cover:
                    link_def += '    xl:cover "'+arc_cover+'" ;\n'

                arc_axis = arc.get('axis', None)
                if arc_axis:
                    link_def += '    xl:axis "'+arc_axis+'" ;\n'

                arc_complement = arc.get('complement', None)
                if arc_complement:
                    link_def += '    xl:complement "'+arc_complement+'" ;\n'

                arc_name = arc.get('name', None)
                if arc_name:
                    link_def += '    xl:name "'+arc_name+'" ;\n'

                arc_use = arc.get('use', None)
                if arc_use:
                    link_def += '    xl:use "prohibited" ;\n'

                arc_priority = arc.get('priority', None)
                if arc_priority:
                    link_def += '    xl:priority "'+ str(arc_priority) + '"^^xsd:integer ;\n'

                arc_order = arc.get('order', None)
                if arc_order:
                    link_def += '    xl:order "'+arc_order+'"^^xsd:decimal ;\n'

                arc_weight = arc.get('weight', None)
                if arc_weight:
                    link_def += '    xl:weight "'+arc_weight+'"^^xsd:decimal ;\n'

                link_def += '    xl:from '+str_subject.lower()+' ;\n'
                link_def += '    xl:to '+str_object.lower()+' ;\n'

                if link_def.lower() not in params['defined_links']:
                    output.write(turtlename(base, "link"+str(params['linkNumber']), ns)+"\n")
                    output.write(link_def)
                    output.write('    .\n')
                    params['defined_links'].append(link_def.lower())

    return params

def turtlename(base, name, ns):

    if 'http' in base:
        return '<'+base+"/"+name+">"
    else:
        return base+":"+name


def getTurtleName(loc, base, ns):

    href = loc.get('href', None)
    if href is not None:
        name = None
        res = findId(href, base, None, name)
        if res is not None:
            prefix = getNsPrefix(ns)
            tname = prefix[0:len(prefix)] + ":" + name
            return tname

    base = base.replace("eu/eu", "eu") # strange difference between actual location and uri
    for key in ns:
        if base.lower() == ns[key].lower():
            base = key

    # locator to a virtual object, e.g. rendering resource
    # that doesn't have a literal value such a string or node
    # this hack as it uses locally scoped labels for names
    if loc['label'][-1]=='.':
        if 'http' in base:
            p = "<"+base+':'+loc['label'][0:-1]+">"
        else:
            p = base+':' + loc['label'][0:-1]
    else:
        if 'http' in base:
            p = "<"+base+':' + loc['label']+">"
        else:
            p = base+':' + loc['label']
    return p

uris = dict()

def findId(uri, base, ns, name):

    # print("findId: uri = "+str(uri)+", base = "+str(base))

    # if (uri[0] != '/') and (uri[0:7] == "http://" != 0):
    #     uri = src.data.expandRelativePath(uri, base)

    # print("searching on key '"+str(uri)+"'")
    found = uri in uris.keys()

    if found:
        # print("found "+str(uri))
        # print("name %s, ns %s\n", found->name, found->ns);
        ns = uris[uri]['ns']
        name = uris[uri]['name']
        return (ns, name)
    return None

def shortRoleName(role, arc, params):

    ns = params['namespaces']

    base, name = splitRole(role)

    return "xbrll:"+name+""

    for key in ns:
        if role == ns[key]:
            return "<"+key+"/"+name+">"

    for key in ns:
        if base == ns[key]:
            base = key

    # if prefix is None:
    #     prefix = arc ? genArcRolePrefixName() : genRolePrefixName()
    #     declareNamespace(fout, prefix, base)
    # else
    #     prefix = _strdup(prefix);

    if "http" in base:
        return "<"+base+"/"+ name+">"
    else: 
        return base+":" + name
    # return None

# generate base, prefix and name from role or arcrole URI
# the generated strings must be freed by the caller
def splitRole(uri):

    base = "/".join(uri.split('/')[0:-1])
    name = uri.split('/')[-1]

    return base, name

arcroleNumber = 0
# used for gensymmed names for nodes
def genArcRolePrefixName():
    global arcroleNumber
    arcroleNumber += 1
    name = "arcrole" + str(arcroleNumber)
    return name

roleNumber = 0

# used for gensymmed names for nodes
def genRolePrefixName():
    global roleNumber
    roleNumber += 1
    name = "role"+str(roleNumber)
    return name

# used for roleRef and arcRoleRef elements to
# declare namespace, and prefix
# def declareRole(uri, arc):
#     base = None
#     name = None
#     splitRole(roleUri, &base, &name)
#     if (!getNsPrefix(base))
#         prefix = arc ? genArcRolePrefixName() : genRolePrefixName()
#         declareNamespace(fout, prefix, base)

# generate base, prefix and name from role or arcrole URI
# the generated strings must be freed by the caller
# def splitRole(roleUri, pbase, pname):

#     l = len(roleUri)
    
#     last = strrchr(roleUri, '/');
#     n = last-roleUri+2;
#     base = roleUri[0:n-1]
#     pbase = base

#     n = roleUri+l-last;
#     name = last[1:n-1]
#     pname = name;
