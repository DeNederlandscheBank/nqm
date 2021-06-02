#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script turns the EIOPA and GLEIF register data into an RDF dataset
in turtle format. The resulting database can queried using the rdflib
package in python and is the basis for the translation machine.
Everything is happening in the main function.

Script is derived from a notebook by Willem Jan Willemse (DNB), with some
additions by Jan-Marc Glowienke.
"""

from os import listdir
from os.path import join, isfile
import pandas as pd
from rdflib import URIRef, term, Graph, Literal, Namespace
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD
from src_eiopa.generator_utils import strip_item

EIOPA_DATA_PATH = join("data", "eiopa", '1_external', 'eiopa')
GLEIF_DATA_PATH = join("data", "eiopa", "1_external", 'gleif')


def write_eiopa_graph():
    """ #TODO: add docstring """
    insurance_names = pd.read_excel(
        join(EIOPA_DATA_PATH, "Insurance_undertaking_names.xlsx"),
        engine='openpyxl')
    register = pd.read_csv(
        join(EIOPA_DATA_PATH, 'DATINS_Export_637439776565055685.csv'), sep=';')

    # Initialize graph with namespace bindings
    g = Graph()

    # Read GLEIF and EIOPA data
    with open(join(GLEIF_DATA_PATH, 'gleif-L1-extract.ttl'), "rb") as fp:
        g.parse(data=fp.read(), format='turtle')
    with open(join(GLEIF_DATA_PATH, 'EntityLegalFormData.ttl'), "rb") as fp:
        g.parse(data=fp.read(), format='turtle')

    print("graph has {} statements.".format(len(g)))

    # Add triples to graph

    eiopa = Graph()

    eiopa.bind('CountryCodes', URIRef(
        'https://www.omg.org/spec/LCC/Countries/'
        'ISO3166-1-CountryCodes-Adjunct/'))
    eiopa.bind('gleif-Base', URIRef('https://www.gleif.org/ontology/Base/'))
    eiopa.bind('eiopa-Base', URIRef("https://eiopa.europe.eu/ontology/Base/"))
    eiopa.bind('owl', OWL)

    gleif_base = Namespace('https://www.gleif.org/ontology/Base/')
    eiopa_base = Namespace("https://eiopa.europe.eu/ontology/Base/")
    eiopa_NCA = Namespace("https://rdf.eiopa.europe.eu/NCA/")

    for idx in register.index:
        row = register.loc[idx]
        if str(row["LEI"]) != 'nan':

            short_name = None
            names = insurance_names[insurance_names['LEI code'] == row['LEI']]
            if not names.empty:
                short_name = names['Verkorte naam'].values[0].lower()

            # find subject with specific LEI
            query = '''
                SELECT ?s ?legalname 
                WHERE {?lei <https://www.gleif.org/ontology/L1/LEI> "''' +\
                    row["LEI"] + '''" . 
                    ?lei <https://www.gleif.org/ontology/L1/identifiesAndRecords> ?s.
                    ?s <https://www.gleif.org/ontology/L1/hasLegalName> ?legalname . }
                    '''
            results = g.query(query)
            if len(results) == 1:
                subj = list(results)[0][0]
                legalname = list(results)[0][1].lower()
                name = legalname.replace(" B.V.", "").replace(" N.V.",
                                                              "").lower()
            else:
                print("lei not found: " + row['LEI'])
                continue    # skip to next LEI code

            # specify that subject is an insurance undertaking
            pred = OWL.a
            obj = eiopa_base.InsuranceUndertaking
            eiopa.add((subj, pred, obj))

            # add register reference to subject
            pred = eiopa_base.hasRegisterIdentifier
            nca = row["Name of NCA"].replace(" ", "-").replace("(", "").replace(
                ")", "")
            idcode = row["Identification code"].replace(" ", "")
            obj = URIRef(
                "https://rdf.eiopa.europe.eu/L1-data/IURI-" + nca + "-" +
                idcode)
            eiopa.add((subj, pred, obj))

            # add register entry
            eiopa.add(
                (obj, OWL.a, eiopa_base.InsuranceUndertakingRegisterIdentifier))
            # add original subject reference to register entry
            eiopa.add((obj, gleif_base.identifies, subj))

            # add specificities of register
            if row["Cross border status"] == 'Domestic undertaking':
                eiopa.add((obj, eiopa_base.hasCrossBorderStatus,
                           Literal(row["Cross border status"])))
                eiopa.add((obj, eiopa_base.hasEUCountryWhereEntityOperates,
                           URIRef(
                               'https://www.omg.org/spec/LCC/Countries/'
                               'ISO3166-1-CountryCodes-Adjunct/' +
                               row["EU Country where the entity operates"])))

                eiopa.add((obj, eiopa_base.hasInsuranceUndertakingID,
                           Literal(row["Identification code"].lower())))
                eiopa.add((obj, eiopa_base.hasNCA, Literal(row["Name of NCA"])))
                eiopa.add(
                    (obj, eiopa_base.hasIdentifyingName, Literal(
                        strip_item(legalname))))
                if legalname != name:
                    eiopa.add(
                        (obj, eiopa_base.hasIdentifyingName, Literal(
                            strip_item(name))))
                if short_name is not None:
                    eiopa.add((obj, eiopa_base.hasIdentifyingName,
                               Literal(strip_item(short_name))))
                eiopa.add((obj, eiopa_base.hasIdentifyingName,
                           Literal(row["Identification code"].lower())))
                eiopa.add((obj, eiopa_base.hasRegistrationStartDate,
                           Literal(row['Registration start date'])))
                if str(row['Registration end date']) != 'nan':
                    eiopa.add((obj, eiopa_base.hasRegistrationEndDate,
                               Literal(row['Registration end date'])))
                eiopa.add((obj, eiopa_base.hasOperationStartDate,
                           Literal(row['Operation Start Date'])))
                if str(row['Operation End Date']) != 'nan':
                    eiopa.add((obj, eiopa_base.hasOperationEndDate,
                               Literal(row['Operation End Date'])))

    with open(join(EIOPA_DATA_PATH, "eiopa_register.ttl"), "wb") as f:
        f.write(eiopa.serialize(format="turtle"))

    print("Job done!")

    return True


if __name__ == "__main__":
    write_eiopa_graph()
