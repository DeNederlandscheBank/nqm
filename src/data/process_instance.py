from io import StringIO, BytesIO
from lxml import etree
from collections import defaultdict

def genReport(params):
    params['report'] = "_:report1"
    params['output'].write(params['report']+"\n")
    params['output'].write('    xl:type xbrll:Report;\n')
    params['output'].write('    xbrll:file "'+params['base']+'".\n')
    return params

def getContext(context, params):
    output = params['output']
    output.write("_:context_"+context.attrib['id']+"\n")
    output.write('    xl:type xbrll:Context ;\n')

    # every context element has one entity element
    # and that must have an identifier and scheme
    # entity element has optional segment
    identifier = context[0][0]
    scheme = identifier.attrib["scheme"]
    # if scheme == "http://standards.iso.org/iso/17442": # we have a lei-code, so map to dnb namespace
    #     output.write('    xbrli:entity <dnb:entity:lei-code:'+identifier.text+'>;\n')
    # else:        
    #     output.write('    xbrli:entity [\n')
    #     segment = getContextNode(context, "segment")
    #     if segment is not None:
    #         xml = segment[0]
    #         output.write('        xbrli:segment """'+xml+'"""^^rdf:XMLLiteral;\n')
    #     output.write('        xbrli:identifier "'+identifier.text+'";\n')
    #     output.write('        xbrli:scheme <'+scheme+'>;\n        ];\n')
    # alternative 2
    segment = getContextNode(context, "segment")
    output.write('    xbrll:Entity <'+scheme+':'+ identifier.text+'> ;\n')

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
            # a scenario may have a typed member with a dimension and a single child element
            if name == 'typedMember':                
                child_child = child.getchildren()[0]
                child_child_namespace = etree.QName(child_child).namespace
                for key in params['namespaces']:
                    if child_child_namespace == params['namespaces'][key]:
                        child_child_namespace = key
                xml += '        xbrll:hasTypedMember [\n            xbrll:hasDimension {} ;\n            {}:{} "{}" ;\n            ] ;\n'.format(
                    child.values()[0], 
                    child_child_namespace,
                    etree.QName(child_child).localname,
                    str(child_child.text).replace('"',"'").lower()
                )
                
            elif child.text is not None:
                xml += '        '+str(namespace)+':'+name+' '+str(child.text).replace('"',"'").lower()+' ;\n'
            else:
                xml += '        '+str(namespace)+':'+name+' "'+str(child.text).replace('"',"'").lower()+'" ;\n'
        output.write('    xbrll:hasScenario [\n'+xml+'        ] ;\n')

    # every context element has one period element
    period = getContextNode(context, 'period')
    child = period[0]
    if etree.QName(child).localname == "instant":
        instant = child.text
        output.write('    xbrll:instant "'+instant+'"^^xsd:date ;\n    .\n')
    elif etree.QName(child).localname == "forever":
        output.write('    xbrll:Period xbrll:forever ;\n    .\n')
    else: # expect sequence of startDate endDate pairs
        output.write('    xbrll:Period (\n')
        while child is not None:
            value = child.text
            output.write('        [ xbrll:startDate "'+value+'"^^xsd:date ;\n')
            child = child.getnext()
            value = child.text
            output.write('          xbrll:endDate "'+value+'"^^xsd:date ; ]\n')
            child = child.getnext()
        output.write('        ) ;\n    .\n')
    return params


def getContextNode(context, localname):
    for node in context:
        if etree.QName(node).localname == localname:
            return node
    return None


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
        output.write('    xbrli:numerator '+numerator+' ;\n')
        output.write('    xbrli:denominator '+denominator+' ;\n    .\n')
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

def getSchemaRef(node, params):
    output = params['output']
    uri = node.attrib.get('{http://www.w3.org/1999/xlink}href', None)
    if uri is None:
        params['log'].write('could not identify schema location\n')
    else:
        params['output'].write("_:schemaRef\n")
        params['output'].write('    xlink:schemaRef <'+uri+'> ;\n')
        params['output'].write('    xbrll:fromReport '+params['report']+' ;\n    .\n')
    return params

def genFactName(params):
    params['fact_count'] += 1
    params['output'].write("_:fact" +str(params['fact_count'])+"\n")
    params['output'].write('    xl:type xbrll:Fact ;\n')
    return params

def getFact(fact, params):
    report = params['report']
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
            child_fact_name.append('_:fact'+str(params['fact_count'])+"\n")
        params = genFactName(params)
        output.write('    xl:type xbrll:Tuple ;\n')
        output.write('    xbrll:fromReport '+report+' ;\n')
        output.write('    xbrll:hasDimension '+namespace+':'+name+' ;\n')
        output.write('    xbrli:content (\n')
        for item in child_fact_name:
            output.write('        '+item+'\n')
        output.write('    ).\n')
    else:
        params = genFactName(params)
        output.write('    xbrll:fromReport '+report+' ;\n')
        output.write('    xbrll:hasDimension '+namespace+':'+name+' ;\n')
        unitRef = fact.attrib.get("unitRef", None)
        if unitRef is not None:
            # numeric fact
            value = fact.text
            if '.' in value:
                dot = "decimal"
            else:
                dot = "integer"
            output.write('    rdf:value "'+value+'"^^xsd:'+dot+' ;\n')
            decimals = fact.attrib.get("decimals", None)
            if decimals is not None:
                output.write('    xbrll:decimals "'+decimals+'"^^xsd:integer ;\n')
            precision = fact.attrib.get("precision", None)
            if precision is not None:
                output.write('    xbrll:precision "'+precision+'"^^xsd:integer ;\n')
            balance = fact.attrib.get("balance", None)
            # if balance is not None:
            #     output.write('    xbrli:balance "'+balance+'"\n')
            output.write('    xbrll:hasUnit _:unit_'+unitRef+' ;\n')
        else: 
            # non-numeric fact
            count = len(fact)
            if count >= 1:
                xml = ''
                for child in fact:
                    xml += etree.tostring(child).replace('"',"'") # use single quotation mark if string has quotation marks
                output.write('    xbrll:Resource """'+xml+'"""^^rdf:XMLLiteral.\n')
            else:
                content = fact.text.replace('"',"'")
                lang = fact.attrib.get("lang", None)
                if lang is not None:
                    output.write('    xbrll:Resource """'+content+'"""@'+lang+' ;\n')
                else:
                    output.write('    xbrll:Resource """'+content+'""" ;\n')
        output.write('    xbrll:hasContext _:context_'+contextRef+' ;\n    .\n')
    return params


def processInstance(root, base, namespaces):
    params = dict()
    params['base'] = base
    params['fact_count'] = 0
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
        if "#" in namespaces[namespace]:
            params['output'].write("@prefix "+namespace.lower()+": <"+namespaces[namespace].lower()+">.\n")
        else:
            params['output'].write("@prefix "+namespace.lower()+": <"+namespaces[namespace].lower()+"/>.\n")
    params['output'].write('\n\n')

    params = genReport(params)

    firstFootNote = None
    for child in root:
        name = etree.QName(child).localname
        namespace = etree.QName(child).namespace
        if name == "context":
            getContext(child, params)
        elif name == "unit":
            getUnit(child, params)
        elif name == "schemaRef":
            getSchemaRef(child, params)
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
