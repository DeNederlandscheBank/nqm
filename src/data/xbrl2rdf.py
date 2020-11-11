
from io import StringIO, BytesIO
from lxml import etree
from collections import defaultdict

def genProvenanceName(params):
    params['provenance_count'] += 1
    params['provenance'] = "_:provenance"+str(params['provenance_count'])
    params['output'].write(params['provenance'])
    params['output'].write('    xl:instance "'+params['base']+'".\n')
    return params

def getContext(context, params):
    output = params['output']
    output.write("_:context_"+context.attrib['id']+"\n")
    output.write("    xl:type xbrli:context;\n")

    # every context element has one entity element
    # and that must have an identifier and scheme
    output.write("    xbrli:entity [\n")

    # entity element has optional segment
    segment = getContextNode(context, "segment")
    if segment is not None:
        xml = segment[0]
        output.write('        xbrli:segment """'+xml+'"""^^rdf:XMLLiteral;\n')

    identifier = getContextIdentifier(context)
    output.write('        xbrli:identifier "'+identifier.text+'";\n')

    scheme = identifier.attrib["scheme"]
    output.write('        xbrli:scheme <'+scheme+'>;\n        ];\n')

    # each context may have one scenario element
    scenario = getContextNode(context, "scenario")
    if scenario is not None:
        xml = ''
        for child in scenario:
            namespace = etree.QName(child).namespace
            for key in params['namespaces']:
                if namespace == params['namespaces'][key]:
                    namespace = key
            name = etree.QName(child).localname
            xml += '        '+str(namespace)+':'+name+' "'+str(child.text)+'"^^rdf:XMLLiteral;\n'
        output.write('    xbrli:scenario [\n'+xml+'        ];\n')

    # every context element has one period element
    period = getContextNode(context, 'period')
    child = period[0]
    if etree.QName(child).localname == "instant":
        instant = child.text
        output.write('    xbrli:instant "'+instant+'"^^xsd:date.\n')
    elif etree.QName(child).localname == "forever":
        output.write('    xbrli:period xbrli:forever.\n')
    else: # expect sequence of startDate endDate pairs
        output.write('    xbrli:period (\n')
        while child is not None:
            value = child.text
            output.write('        [ xbrli:startDate "'+value+'"^^xsd:date;\n')
            child = child.getnext()
            value = child.text
            output.write('          xbrli:endDate "'+value+'"^^xsd:date; ]\n')
            child = child.getnext()
        output.write('        ).\n')
    return params


def getContextNode(context, localname):
    for node in context:
        if etree.QName(node).localname == localname:
            return node
    return None


def getContextIdentifier(context):
    entity = context[0]
    return entity[0]


def getUnit(unit, params):
    output = params['output']
    unit_id = unit.attrib['id']
    count = len(unit)
    child = unit[0]
    if ((child is not None) and (etree.QName(child).localname == "measure")):
        measure = child.text
        if ":" in measure:
            output.write('_:unit_'+unit_id+' xbrli:measure '+measure+'.\n')
        else:
            output.write('_:unit_'+unit_id+' xbrli:measure xbrli:'+measure+'.\n')
    elif etree.QName(child).localname == "divide":
        numerator = getNumerator(child)
        denominator = getDenominator(child)
        output.write('_:unit_'+unit_id+'\n')
        output.write('    xbrli:numerator '+numerator+';\n')
        output.write('    xbrli:denominator '+denominator+'.\n')
    return params


def getNumerator(divide):
    for child in divide:
        if etree.QName(node).localname == "unitNumerator":
            child = child[0]
            if child is not None:
                content = child.text
            return content
    return None


def getDenominator(divide):
    for child in divide:
        if etree.QName(node).localname == "unitDenominator":
            child = child[0]
            if child is not None:
                content = child.text
            return content
    return None


def genFactName(params):
    params['fact_count'] += 1
    params['output'].write("_:fact" +str(params['fact_count']))
    return params

def getFact(fact, params):
    provenance = params['provenance']
    base = params['base']
    fact_count = params['fact_count']
    output = params['output']
    fact_id = fact.attrib.get("id", None)
#     if fact_id:
#         addId(base, (const char *)id, (char *)(fact->ns->href), (const char *)fact->name);
    name = etree.QName(fact).localname
    namespace = etree.QName(fact).namespace
    for key in params['namespaces']:
        if namespace == params['namespaces'][key]:
            namespace = key
    if namespace is None:
        namespace = ''
    contextRef = fact.attrib.get("contextRef", None)
    if contextRef is None:
        child_fact_name = []
        for child in fact:
            params = getFact(child, params)
            child_fact_name.append('_:fact'+str(params['fact_count']))
        params = genFactName(params)
        output.write('    xl:type xbrli:tuple;\n')
        output.write('    xl:provenance '+provenance+';\n')
        output.write('    rdf:type '+namespace+':'+name+';\n')
        output.write('    xbrli:content (\n')
        for item in child_fact_name:
            output.write('        '+item+'\n')
        output.write('    ).\n')
        return params
    params = genFactName(params)
    output.write('    xl:type xbrli:fact;\n')
    output.write('    xl:provenance '+provenance+';\n')
    output.write('    rdf:type '+namespace+':'+name+';\n')
    unitRef = fact.attrib.get("unitRef", None)
    if unitRef is not None:
        # numeric fact
        value = fact.text
        if '.' in value:
            dot = "decimal"
        else:
            dot = "integer"
        output.write('    rdf:value "'+value+'"^^xsd:'+dot+';\n')
        decimals = fact.attrib.get("decimals", None)
        if decimals is not None:
            output.write('    xbrli:decimals "'+decimals+'"^^xsd:integer;\n')
        precision = fact.attrib.get("precision", None)
        if precision is not None:
            output.write('    xbrli:precision "'+precision+'"^^xsd:integer;\n')
        balance = fact.attrib.get("balance", None)
        if balance is not None:
            output.write('    xbrli:balance "'+balance+'"\n')
        output.write('    xbrli:unit _:unit_'+unitRef+';\n')
    else: 
        # non-numeric fact
        count = len(fact)
        if count >= 1:
            xml = ''
            for child in fact:
                xml += etree.tostring(child)
            output.write('    xbrli:resource """'+xml+'"""^^rdf:XMLLiteral.\n')
        else:
            content = fact.text
            lang = fact.attrib.get("lang", None)
            if lang is not None:
                output.write('    xbrli:resource """'+content+'"""@'+lang+';\n')
            else:
                output.write('    xbrli:resource """'+content+'""";\n')
    output.write('    xbrli:context _:context_'+contextRef+'.\n')
    return params


def processInstance(root, base, namespaces):
    params = dict()
    params['base'] = base
    params['fact_count'] = 0
    params['provenance_count'] = 0
    params['namespaces'] = namespaces
    params['output'] = StringIO()
    params['log'] = StringIO()

    if etree.QName(root).localname == "schema":
        print("schema") # to do
    if etree.QName(root[0]).localname == "linkbase":
        print("linkbase") # to do

    params['log'].write('processing instance \n')
    params['output'].write('# RDF triples (in turtle syntax) imported from XBRL resource at URI\n')
    params['output'].write('# '+str(params['base'])+'\n\n')

    params['output'].write('# the namespaces\n')
    for namespace in namespaces.keys():
        params['output'].write("@prefix "+namespace+": <"+namespaces[namespace]+">.\n")
    params['output'].write('\n\n')

    params = genProvenanceName(params)

    firstFootNote = None
    for child in root:
        name = etree.QName(child).localname
        namespace = etree.QName(child).namespace
        if name == "context":
            getContext(child, params)
        elif name == "unit":
            getUnit(child, params)
        elif name == "schemaRef":
            uri = child.attrib.get('{http://www.w3.org/1999/xlink}href', None)
            if uri is None:
                params['log'].write('could not identify schema location\n')
                return -1;
#             res = prependDtsQueue(XBRL_SCHEMA, (const char *)uri, base, ns, 0);
        elif name == "footnoteLink":
            if firstFootNote is None:
                firstFootNote = child;
        else:
            params = getFact(child, params)

    if firstFootNote is not None:
        for child in firstFootNote:
            if etree.QName(child).localname == "footnoteLink":
                params['log'].write('footnote base = '+base+', ns ='+ns+'%s\n')
    #             processExtendedLink(child, base, "");
            
    return params

def processLinkBase(root, base, ns):

    # print("checking linkbase " + base + "\n")

    for node in root:

        node_type = node.attrib.get('{http://www.w3.org/1999/xlink}type', None)

        if node_type == 'extended':
            checkExtendedLink(node, base, ns)
        elif node_type == "simple":
            checkSimpleLink(node, base, ns)

    # print("processing linkbase " + base)

    for node in root:

        node_type = node.attrib.get('{http://www.w3.org/1999/xlink}type', None)

        if node_type == "extended":
            processExtendedLink(node, base, ns)
        elif node_type == "simple":
            processSimpleLink(node, base, ns)

    return None

def checkSimpleLink(node, base, ns):

    missingSchemas = 0
    # print("checking simple link " + str(node.tag))
    
    href = node.attrib.get('{http://www.w3.org/1999/xlink}href', None)

    if href:
        uri = href
        p = uri.split("#")[1]

        # lns = (ns && strncmp((char *)href, "http://", 7) ? ns : NULL)

        # // returns false if uri has already been processed
        # if (!prependDtsQueue(XBRL_SCHEMA, (const char *)uri, base, lns, 0))
        #     ++missingSchemas;
        #     print("found unseen1: "+ uri)
    return missingSchemas

def checkExtendedLink(node, base, ns):

    missingSchemas = 0
    # print("checking extended link " + str(node.tag))

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

    return missingSchemas

# simple links are used to point to linkbases and taxonomy schemas
# with the xlink:href attribute. If defined use xml:base in place
# of the document URI for resolving relative links. The xlink:role
# attribute may be used to describe the link's role. I am unsure as
# to whether simple links add triples or just aid in Dts discovery

def processSimpleLink(node, base, ns):

    res = -1
    # print("processing simple link "+ str(node))

    node_role = node.attrib.get('{http://www.w3.org/1999/xlink}role', None)

    if node_role is not None:
        declareRole(role, 0)

    node_role = node.attrib.get('arcrole', None)

    if node_role is not None:
        declareRole(role, 1)

    return res

def processExtendedLink(element, base, ns):
    # localLocCount = 0
    # prevLoc = None
    # resCount = 0
    nodes_labels = defaultdict(list)
    labels_nodes = defaultdict(list)

    locators = dict()
    arcs = list()

    for node in element:
        # localLocCount += 1

        node_type = node.attrib['{http://www.w3.org/1999/xlink}type']
        if node_type == 'locator':
            # locCount += 1
            # localLocCount += 1 
            #addLabel((char *)(loc->label), loc);
            locators[node] = {'href': node.attrib.get('{http://www.w3.org/1999/xlink}href', None),
                              'role': node.attrib.get('{http://www.w3.org/1999/xlink}role', None),
                              'title': node.attrib.get('{http://www.w3.org/1999/xlink}title', None),
                              'label': node.attrib.get('{http://www.w3.org/1999/xlink}label', None)}

            # if xlink->loc:
            #     xlink->lastLoc->next = loc;
            # else
            #     xlink->loc = loc;

            # xlink->lastLoc = loc;

        elif node_type == 'resource':
            # resCount += 1
            # localLocCount += 1
            # loc_prev = prevLoc
            # prevLoc = loc

            locators[node] = {'lang': node.attrib.get('{http://www.w3.org/1999/xlink}lang', None),
                              'role': node.attrib.get('{http://www.w3.org/1999/xlink}role', None),
                              'title': node.attrib.get('{http://www.w3.org/1999/xlink}title', None),
                              'label': node.attrib.get('{http://www.w3.org/1999/xlink}label', None)}

            #addLabel((char *)(loc->label), loc);

            # if (node->children)
            #     loc->node = node;

            # if (xlink->loc)
            #     xlink->lastLoc->next = loc;
            # else
            #     xlink->loc = loc;

            # xlink->lastLoc = loc;
        elif node_type == "arc":
            # arcCount += 1
            # arc_prevLoc = prevLoc

            arc_dict = {'node': node,
                         'fromlabel': node.attrib.get('{http://www.w3.org/1999/xlink}from', None),
                         'tolabel': node.attrib.get('{http://www.w3.org/1999/xlink}to', None),
                         'role': node.attrib.get('{http://www.w3.org/1999/xlink}arcrole', None),
                         'title': node.attrib.get('{http://www.w3.org/1999/xlink}title', None)}

            order = node.attrib.get("order", None)
            if order is not None:
                arc_dict['order'] = order

            use = node.attrib.get('use', None)
            if use is not None:
                arc_dict['use'] = use
            # arc->use = (use && samestring(use, "prohibited") ? 1 : 0);

            priority = node.attrib.get('priority', None)
            if priority is not None:
                arc_dict['priority'] = priority

            weight = node.attrib.get("weight", None)
            if weight is not None:
                arc_dict['weight'] = weight

            # if (xlink->arc)
            #     xlink->lastArc->next = arc;
            # else
            #     xlink->arc = arc;

            # xlink->lastArc = arc;

            arcs.append(arc_dict)

    for locator in locators.keys():    # if locator is not None:
        nodes_labels[locator].append(locators[locator]['label'])
        labels_nodes[locators[locator]['label']].append(locator)
        # addLabel((char *)(loc->label), loc);;

    # now fix up pointers between arcs and locs
    for arc in arcs:
        arc['fromloc'] = list()
        label = arc['fromlabel']
        if label in labels_nodes.keys():
            arc['fromloc'] = labels_nodes[label]
        arc['toloc'] = list()
        label = arc['tolabel']
        if label in labels_nodes.keys():
            arc['toloc'] = labels_nodes[label]

    # now translate xlink into turtle
    translateXLink(element, arcs, locators, base, ns);

    return None

linkNumber = 0

def translateXLink(node, arcs, locators, base, ns):

    xlink_role = node.attrib.get('{http://www.w3.org/1999/xlink}role', None)
    xlink_id = node.attrib.get('id', None)
    xlink_base = node.attrib.get('base', None)

    print("# "+str(node.tag)+" with role " + str(xlink_role))

    # footnoteLink has xlink:role="http://www.xbrl.org/2003/role/link"
    # which isn't really worth noting in the RDF, so suppress it here

    for arc in arcs:
        for fromloc in arc['fromloc']:
            for toloc in arc['toloc']:

                global linkNumber
                linkNumber += 1

                str_subject = getTurtleName(locators[fromloc], base, ns)
                str_predicate = shortRoleName(arc['role'], 1, ns)
                str_object = getTurtleName(locators[toloc], base, ns)

                print("_:link" + str(linkNumber) + " " + str(str_predicate) + "[")
                print("    xl:type xl:link;")

                if xlink_role is not None:
                    print("    xl:role "+xlink_role+";")

                toloc_role = locators[toloc].get('role', None)
                if toloc_role:
                    role = shortRoleName(toloc_role, 0, ns)
                    print("    xlink:role "+toloc_role+";")

                toloc_lang = locators[toloc].get('lang', None)
                if (toloc_lang):
                    print('    rdf:lang "'+toloc_lang+'";')

                arc_use = arc.get('use', None)
                if arc_use:
                    print('    xl:use "prohibited";')

                arc_priority = arc.get('priority', None)
                if arc_priority:
                    print('    xl:priority "'+ str(arc_priority) + '"^^xsd:integer;')

                arc_order = arc.get('order', None)
                if arc_order:
                    print('    xl:order "'+arc_order+'"^^xsd:decimal;')

                print("    xl:from "+str_subject+ ";")

                arc_weight = arc.get('weight', None)
                if arc_weight:
                    print('    xl:weight "'+arc_weight+'"^^xsd:decimal;')

                node = toloc
                if node is not None:
                    count = len(node)
                    if count >= 1:
                        xml = ''
                        for child in node:
                            xml += str(child.text)
                        print('    rdf:value """'+str(xml)+'"""^^rdf:XMLLiteral;')
                    else:
                        content = node.text
                        toloc_lang = locators[toloc].get('lang', None)
                        if toloc_lang:
                            print('    rdf:value """'+str(content)+'"""@'+toloc_lang+';')
                        else:
                            print('    rdf:value """'+str(content)+'""";')
                else:
                    print("    xl:to "+str_object+";")

                print("    ].")

    return None

def getTurtleName(node, base, ns):

    href = node.get('href', None)

    if href is not None:

        return href

        namespace = etree.QName(node).namespace
        name = etree.QName(node).localname
        
        # int res = findId((char *)(loc->href), base, &ns, &name);

        # if res == 0:
        tname = namespace + ":" + name
        return tname

        # print("href = %s\nlabel =%s\nnamespace = %s\nbase = %s\n", loc->href, loc->label, ns, base);

    # locator to a virtual object, e.g. rendering resource
    # that doesn't have a literal value such a string or node
    # this hack as it uses locally scoped labels for names
    return "_:"+ str(node.get('label', None))

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

    return base + ":" + name
    # return None

# generate base, prefix and name from role or arcrole URI
# the generated strings must be freed by the caller
def splitRole(roleUri):

    pbase = "/".join(roleUri.split('/')[0:-1])
    pname = roleUri.split('/')[-1]

    return pbase, pname

# // used for gensymmed names for nodes
# char *genArcRolePrefixName()
# {
#     static int arcroleNumber = 0;
#     char *name = calloc(1, 20);
#     assert(name);
#     sprintf_s(name, "arcrole%d", ++arcroleNumber);
#     return name;
# }

# // used for gensymmed names for nodes
# char *genRolePrefixName()
# {
#     static int roleNumber = 0;
#     char *name = calloc(1, 16);
#     assert(name);
#     sprintf_s(name, "role%d", ++roleNumber);
#     return name;
# }

# // used for roleRef and arcRoleRef elements to
# // declare namespace, and prefix
# void declareRole(const char *roleUri, int arc)
# {
#     char *base = NULL;
#     char *name = NULL;
#     assert(roleUri);
#     splitRole(roleUri, &base, &name);

#     if (!getNsPrefix(base))
#     {
#         char *prefix = arc ? genArcRolePrefixName() : genRolePrefixName();
#         assert(prefix);
#         assert(base);
#         declareNamespace(fout, prefix, base);
#         free(prefix);
#     }

#     free(base);
#     free(name);
# }

# // generate base, prefix and name from role or arcrole URI
# // the generated strings must be freed by the caller
# void splitRole(const char *roleUri, char **pbase, char **pname)
# {
#     assert(roleUri);
#     int n, len = strlen(roleUri);
#     char *last = strrchr(roleUri, '/');
#     assert(last);

#     n = last-roleUri+2;
#     char *base = malloc(n);
#     memcpy(base, roleUri, n-1);
#     base[n-1] = '\0';
#     *pbase = base;
#     assert(base);

#     n = roleUri+len-last;
#     char *name = malloc(n);
#     memcpy(name, last+1, n-1);
#     name[n-1] = '\0';
#     *pname = name;
#     assert(name);
# }
