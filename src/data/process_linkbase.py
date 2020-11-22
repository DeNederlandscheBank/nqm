from io import StringIO, BytesIO
from lxml import etree
from collections import defaultdict
import src.data

def processLinkBase(element, params):

    if 'output' not in params.keys():
        params['output'] = StringIO()
    if 'log' not in params.keys():
        params['log'] = StringIO()
    ns = params['namespaces']
    base = params['base']
 
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

        # lns = (ns && strncmp((char *)href, "http://", 7) ? ns : NULL)

        # // returns false if uri has already been processed
        # if (!prependDtsQueue(XBRL_SCHEMA, (const char *)uri, base, lns, 0))
        #     ++missingSchemas;
        #     print("found unseen1: "+ uri)

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

# simple links are used to point to linkbases and taxonomy schemas
# with the xlink:href attribute. If defined use xml:base in place
# of the document URI for resolving relative links. The xlink:role
# attribute may be used to describe the link's role. I am unsure as
# to whether simple links add triples or just aid in Dts discovery

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

            locator = {'href': child.attrib.get('{http://www.w3.org/1999/xlink}href', None),
                       'role': child.attrib.get('{http://www.w3.org/1999/xlink}role', None),
                       'title': child.attrib.get('{http://www.w3.org/1999/xlink}title', None),
                       'label': child.attrib.get('{http://www.w3.org/1999/xlink}label', None)}

            xlink['locators'].append(locator)

            # if xlink->loc:
            #     xlink->lastLoc->next = loc;
            # else
            #     xlink->loc = loc;

            # xlink->lastLoc = loc;

        elif child_type == 'resource':

            resource = {'node': child,
                        'lang': child.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', None),
                        'role': child.attrib.get('{http://www.w3.org/1999/xlink}role', None),
                        'title': child.attrib.get('{http://www.w3.org/1999/xlink}title', None),
                        'label': child.attrib.get('{http://www.w3.org/1999/xlink}label', None),
                        'type': child.attrib.get('{http://www.w3.org/1999/xlink}type', None)}

            xlink['locators'].append(resource)

            # if (node->children)
            #     loc->node = node;

            # if (xlink->loc)
            #     xlink->lastLoc->next = loc;
            # else
            #     xlink->loc = loc;

            # xlink->lastLoc = loc;
        elif child_type == "arc":

            arc = {'fromlabel': child.attrib.get('{http://www.w3.org/1999/xlink}from', None),
                   'tolabel': child.attrib.get('{http://www.w3.org/1999/xlink}to', None),
                   'role': child.attrib.get('{http://www.w3.org/1999/xlink}arcrole', None),
                   'title': child.attrib.get('{http://www.w3.org/1999/xlink}title', None)}

            order = child.attrib.get("order", None)
            if order is not None:
                arc['order'] = order

            use = child.attrib.get('use', None)
            if use is not None:
                arc['use'] = use
            # arc->use = (use && samestring(use, "prohibited") ? 1 : 0);

            priority = child.attrib.get('priority', None)
            if priority is not None:
                arc['priority'] = priority

            weight = child.attrib.get("weight", None)
            if weight is not None:
                arc['weight'] = weight

            xlink['arcs'].append(arc)

            # if (xlink->arc)
            #     xlink->lastArc->next = arc;
            # else
            #     xlink->arc = arc;

            # xlink->lastArc = arc;

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

    # translate xlink into turtle
    translateXLink(node, xlink['arcs'], xlink['locators'], params)

    return params

def translateXLink(node, arcs, locators, params):

    ns = params['namespaces']
    base = params['base']
    output = params['output']

    xlink_role = node.attrib.get('{http://www.w3.org/1999/xlink}role', None)
    xlink_id = node.attrib.get('id', None)
    xlink_base = node.attrib.get('base', None)

    output.write("# localname: "+str(etree.QName(node.tag).localname)+" with role "+str(xlink_role) + "\n")
    output.write("# base     : "+str(base)+"\n")

    # footnoteLink has xlink:role="http://www.xbrl.org/2003/role/link"
    # which isn't really worth noting in the RDF, so suppress it here

    for arc in arcs:
        for fromloc in arc['fromloc']:
            for toloc in arc['toloc']:

                params['linkNumber'] += 1

                str_subject = getTurtleName(fromloc, base, ns)
                str_predicate = shortRoleName(arc['role'], 1, ns)
                str_object = getTurtleName(toloc, base, ns)

                output.write("_:link"+str(params['linkNumber'])+" "+str(str_predicate)+"[\n")
                output.write("    xl:type xl:link;\n")

                if xlink_role is not None:
                    role = shortRoleName(xlink_role, 0, ns)
                    output.write("    xl:role "+role+";\n")

                toloc_role = toloc.get('role', None)
                if toloc_role:
                    role = shortRoleName(toloc_role, 0, ns)
                    output.write("    xlink:role "+role+";\n")

                toloc_lang = toloc.get('lang', None)
                if (toloc_lang):
                    output.write('    rdf:lang "'+toloc_lang+'";\n')

                arc_use = arc.get('use', None)
                if arc_use:
                    output.write('    xl:use "prohibited";\n')

                arc_priority = arc.get('priority', None)
                if arc_priority:
                    output.write('    xl:priority "'+ str(arc_priority) + '"^^xsd:integer;\n')

                arc_order = arc.get('order', None)
                if arc_order:
                    output.write('    xl:order "'+arc_order+'"^^xsd:decimal;\n')

                output.write("    xl:from "+str_subject+ ";\n")

                arc_weight = arc.get('weight', None)
                if arc_weight:
                    output.write('    xl:weight "'+arc_weight+'"^^xsd:decimal;\n')

                node = toloc.get("node", None)
                if node is not None:
                    count = len(node)
                    if count >= 1:
                        xml = ''
                        for child in node:
                            xml += str(child.text)
                        output.write('    rdf:value """'+str(xml)+'"""^^rdf:XMLLiteral;\n')
                    else:
                        content = node.text
                        toloc_lang = toloc.get('lang', None)
                        if toloc_lang:
                            output.write('    rdf:value """'+str(content)+'"""@'+toloc_lang+';\n')
                        else:
                            output.write('    rdf:value """'+str(content)+'""";\n')
                else:
                    output.write("    xl:to "+str_object+";\n")

                output.write("    ].\n")

    return params

def getTurtleName(loc, base, ns):

    href = loc.get('href', None)
    if href is not None:
        ns = None
        name = None
        res = findId(href, base, ns, name)
        if res is not None:
            prefix = getNsPrefix(ns)
            tname = prefix[0:len(prefix)] + ":" + name
            return tname
        # print("href = "+str(href)+"\nlabel = "+ str(loc['label'])+"\nnamespace = "+"ns"+"\nbase = "+str(base)+"\n")

    # locator to a virtual object, e.g. rendering resource
    # that doesn't have a literal value such a string or node
    # this hack as it uses locally scoped labels for names
    if loc['label'][-1]=='.':
        p = '_:' + loc['label'][0:-1]
    else:
        p = '_:' + loc['label']
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

def shortRoleName(role, arc, ns):

    base, name = splitRole(role)

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
