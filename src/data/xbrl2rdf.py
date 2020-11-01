from io import StringIO, BytesIO
from lxml import etree

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
        while (child):
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
            uri = child.attrib['{http://www.w3.org/1999/xlink}href']
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

