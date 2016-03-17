# CTD2rdf.py
#
# Convert the Chemical-disease associations obtained from 
# http://ctdbase.org/downloads/;jsessionid=5B217AB40F810F712C8976BDE2040DC9#cd
# to Open Annotation Data (CTD_chemicals_diseases.tsv.gz)
#
# Author: Charles Kronk
# 2016





# INSTRUCTIONS:
# (1) Go to http://ctdbase.org
# (2) Click on "Download", then on "Data Files" from the dropdown
#     menu.
# (3) Scroll down to "Chemical-disease associations".
# (4) Click on and download "CTD_chemicals.tsv.gz".
# (5) Extract the file "CTD_chemicals.tsv" to the "CTD" folder within LAERTES.
# (6) Run this script as "python CTD2rdf.py".
# (7) This script currently takes longer than 10 minutes to run, but
#     will produce the file "chemical-disease-ctd.nt" upon completion.





# "CTD_chemicals.tsv" contains the following fields:
# (1) ChemicalName
# (2) ChemicalID (MeSH identifier)
# (3) CasRN (CAS Registry Number, if available)
# (4) DiseaseName
# (5) DiseaseID (MeSH or OMIM identifier) 
# (6) DirectEvidence ('|'-delimited list)
# (7) InferenceGeneSymbol
# (8) InferenceScore
# (9) OmimIDs ('|'-delimited list)
# (10) PubMedIDs ('|'-delimited list)
#
# NOTE: These fields apply to the December 2015 CTD data release.

# Debugging info:
#  This script skips the first 28 lines as "header", this may
#  be different in other releases besides the December 2015 release.

import sys
sys.path = sys.path + ['.']
reload(sys)
sys.setdefaultencoding('utf8')


import re, codecs, uuid, datetime
import json
import pickle
from rdflib import Graph, Literal, Namespace, URIRef, RDF, RDFS

DATA_FILE = "CTD_chemicals_diseases.tsv"
(CHEMICAL_NAME,CHEMICAL_ID,CAS_RN,DISEASE_NAME,DISEASE_ID,DIRECT_EVIDENCE,INFERENCE_GENE_SYMBOL,INFERENCE_SCORE,OMIM_IDS,PUBMED_IDS) = range(0,10)


# TERMINOLOGY MAPPING FILES
# MESH_TO_MEDDRA = "../terminology-mappings/MeSHToMedDRA/meshToMeddra-partial-05202014.txt" # This doesn't appear complete?
# MESH_TO_RXNORM = "../terminology-mappings/RxNorm-to-MeSH/mesh-to-rxnorm-standard-vocab-v5.txt"
RXNORM_TO_OMOP = "../terminology-mappings/StandardVocabToRxNorm/imeds_drugids_to_rxcuis.csv"
MEDDRA_TO_OMOP = "../terminology-mappings/StandardVocabToMeddra/standard_vocab_to_meddra.csv"
MESH_TO_OMOP = "../terminology-mappings/StandardVocabToMeSH/mesh-to-standard-vocab-v5.txt"

# OUTPUT DATA FILE
OUTPUT_FILE = "chemical-disease-ctd.nt"

# MESH_D_RXNORM = {}
# f = open(MESH_TO_RXNORM,"r")
# buf = f.read()
# f.close()
# l = buf.split("\n")
# for elt in l:
#    if elt.strip() == "":
#        break

#    (mesh,source_concept_name,rxnorm,concept_name,omop,concept_class_id) = [x.strip() for x in elt.split("|")]
#    MESH_D_RXNORM[mesh] = omop

# Do you really need this?
# Merge integrated sources file eventually.
# MESH_D_MEDDRA = {}
# f = open(MESH_TO_MEDDRA,"r")
# buf = f.read()
# f.close()
# l = buf.split("\n")
# for elt in l:
#    if elt.strip() == "":
#        break
#
#    (mesh,meddra) = [x.strip() for x in elt.split("\t")]
#    MESH_D_MEDDRA[mesh] = meddra

DRUGS_D_OMOP = {}
f = open(RXNORM_TO_OMOP,"r")
buf = f.read()
f.close()
l = buf.split("\n")
for elt in l:
    if elt.strip() == "":
        break

    (omop,rxcui) = [x.strip() for x in elt.split("|")]
    DRUGS_D_OMOP[omop] = rxcui

MEDDRA_D_OMOP = {}
f = open(MEDDRA_TO_OMOP,"r")
buf = f.read()
f.close()
l = buf.split("\n")
for elt in l[1:]:
    if elt.strip() == "":
        break

    (omop,meddra) = [x.strip() for x in elt.split("|")]
    MEDDRA_D_OMOP[omop] = meddra

MESH_D_OMOP = {}
f = open(MESH_TO_OMOP,"r")
buf = f.read()
f.close()
l = buf.split("\n")
for elt in l[1:]:
    if elt.strip() == "":
        break

    (omop,concept_name,mesh) = [x.strip() for x in elt.split("|")]
    MESH_D_OMOP[mesh] = omop


## set up RDF graph
# identify namespaces for other ontologies to be used                                                                                    
dcterms = Namespace("http://purl.org/dc/terms/")
pav = Namespace("http://purl.org/pav")
dctypes = Namespace("http://purl.org/dc/dcmitype/")
sio = Namespace('http://semanticscience.org/resource/')
oa = Namespace('http://www.w3.org/ns/oa#')
aoOld = Namespace('http://purl.org/ao/core/') # needed for AnnotationSet and item until the equivalent is in Open Data Annotation
cnt = Namespace('http://www.w3.org/2011/content#')
siocns = Namespace('http://rdfs.org/sioc/ns#')
swande = Namespace('http://purl.org/swan/1.2/discourse-elements#')
ncbit = Namespace('http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#')
mesh = Namespace('http://purl.bioontology.org/ontology/MESH/')
meddra = Namespace('http://purl.bioontology.org/ontology/MEDDRA/')
rxnorm = Namespace('http://purl.bioontology.org/ontology/RXNORM/')
pubmed = Namespace('http://www.ncbi.nlm.nih.gov/pubmed/')
dailymed = Namespace('http://dbmi-icode-01.dbmi.pitt.edu/linkedSPLs/vocab/resource/')
ohdsi = Namespace('http://purl.org/net/ohdsi#')
poc = Namespace('http://purl.org/net/nlprepository/ohdsi-adr-eu-spc-poc#')

graph = Graph()
graph.namespace_manager.reset()
graph.namespace_manager.bind("dcterms", "http://purl.org/dc/terms/")
graph.namespace_manager.bind("pav", "http://purl.org/pav");
graph.namespace_manager.bind("dctypes", "http://purl.org/dc/dcmitype/")
graph.namespace_manager.bind('sio', 'http://semanticscience.org/resource/')
graph.namespace_manager.bind('oa', 'http://www.w3.org/ns/oa#')
graph.namespace_manager.bind('aoOld', 'http://purl.org/ao/core/') # needed for AnnotationSet and item until the equivalent is in Open Data Annotation
graph.namespace_manager.bind('cnt', 'http://www.w3.org/2011/content#')
graph.namespace_manager.bind('siocns','http://rdfs.org/sioc/ns#')
graph.namespace_manager.bind('swande','http://purl.org/swan/1.2/discourse-elements#')
graph.namespace_manager.bind('ncbit','http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#')
graph.namespace_manager.bind('mesh', 'http://purl.bioontology.org/ontology/MESH/')
graph.namespace_manager.bind('meddra','http://purl.bioontology.org/ontology/MEDDRA/')
graph.namespace_manager.bind('rxnorm','http://purl.bioontology.org/ontology/RXNORM/')
graph.namespace_manager.bind('pubmed', 'http://www.ncbi.nlm.nih.gov/pubmed/')
graph.namespace_manager.bind('dailymed', 'http://dbmi-icode-01.dbmi.pitt.edu/linkedSPLs/vocab/resource/')
graph.namespace_manager.bind('ohdsi', 'http://purl.org/net/ohdsi#')
graph.namespace_manager.bind('poc','http://purl.org/net/nlprepository/ohdsi-adr-eu-spc-poc#')

## TODO: add datatype=XSD.string to all string Literals and port queries appropriately

### open annotation ontology properties and classes
graph.add((dctypes["Collection"], RDFS.label, Literal("Collection"))) # Used in lieau of the AnnotationSet https://code.google.com/p/annotation-ontology/wiki/AnnotationSet
graph.add((dctypes["Collection"], dcterms["description"], Literal("A collection is described as a group; its parts may also be separately described. See http://dublincore.org/documents/dcmi-type-vocabulary/#H7")))

graph.add((oa["Annotation"], RDFS.label, Literal("Annotation")))
graph.add((oa["Annotation"], dcterms["description"], Literal("Typically an Annotation has a single Body (oa:hasBody), which is the comment or other descriptive resource, and a single Target (oa:hasTarget) that the Body is somehow 'about'. The Body provides the information which is annotating the Target. See  http://www.w3.org/ns/oa#Annotation")))

graph.add((oa["annotatedBy"], RDFS.label, Literal("annotatedBy")))
graph.add((oa["annotatedBy"], RDF.type, oa["objectproperties"]))

graph.add((oa["annotatedAt"], RDFS.label, Literal("annotatedAt")))
graph.add((oa["annotatedAt"], RDF.type, oa["dataproperties"]))

graph.add((oa["TextQuoteSelector"], RDFS.label, Literal("TextQuoteSelector")))
graph.add((oa["TextQuoteSelector"], dcterms["description"], Literal("A Selector that describes a textual segment by means of quoting it, plus passages before or after it. See http://www.w3.org/ns/oa#TextQuoteSelector")))

graph.add((oa["hasSelector"], RDFS.label, Literal("hasSelector")))
graph.add((oa["hasSelector"], dcterms["description"], Literal("The relationship between a oa:SpecificResource and a oa:Selector. See http://www.w3.org/ns/oa#hasSelector")))

graph.add((oa["SpecificResource"], RDFS.label, Literal("SpecificResource")))
graph.add((oa["SpecificResource"], dcterms["description"], Literal("A resource identifies part of another Source resource, a particular representation of a resource, a resource with styling hints for renders, or any combination of these. See http://www.w3.org/ns/oa#SpecificResource")))

# these predicates are specific to SPL annotation
graph.add((sio["SIO_000628"], RDFS.label, Literal("refers to")))
graph.add((sio["SIO_000628"], dcterms["description"], Literal("refers to is a relation between one entity and the entity that it makes reference to.")))

graph.add((sio["SIO_000563"], RDFS.label, Literal("describes")))
graph.add((sio["SIO_000563"], dcterms["description"], Literal("describes is a relation between one entity and another entity that it provides a description (detailed account of)")))

graph.add((sio["SIO_000338"], RDFS.label, Literal("specifies")))
graph.add((sio["SIO_000338"], dcterms["description"], Literal("A relation between an information content entity and a product that it (directly/indirectly) specifies")))

graph.add((poc['MeshDrug'], RDFS.label, Literal("MeSH Drug code")))
graph.add((poc['MeshDrug'], dcterms["description"], Literal("Drug code in the MeSH vocabulary.")))

graph.add((poc['ImedsDrug'], RDFS.label, Literal("IMEDS Drug code")))
graph.add((poc['ImedsDrug'], dcterms["description"], Literal("Drug code in the IMEDS standard vocabulary.")))

graph.add((poc['RxnormDrug'], RDFS.label, Literal("Rxnorm Drug code")))
graph.add((poc['RxnormDrug'], dcterms["description"], Literal("Drug code in the Rxnorm vocabulary.")))

graph.add((poc['MeshHoi'], RDFS.label, Literal("MeSH HOI code")))
graph.add((poc['MeshHoi'], dcterms["description"], Literal("HOI code in the MeSH vocabulary.")))

graph.add((poc['ImedsHoi'], RDFS.label, Literal("Imeds HOI code")))
graph.add((poc['ImedsHoi'], dcterms["description"], Literal("HOI code in the IMEDS vocabulary.")))

graph.add((poc['MeddraHoi'], RDFS.label, Literal("Meddra HOI code")))
graph.add((poc['MeddraHoi'], dcterms["description"], Literal("HOI code in the Meddra vocabulary.")))

graph.add((poc['adrSectionIdentified'], RDFS.label, Literal("SPL section location of ADR")))
graph.add((poc['adrSectionIdentified'], dcterms["description"], Literal("SPL section location of the ADR.")))

################################################################################

annotationSetCntr = 1
annotationItemCntr = 1
annotationBodyCntr = 1
annotationEvidenceCntr = 1

annotatedCache = {} # indexes annotation ids so that multiple bodies can be attached
currentAnnotation = annotationItemCntr

currentAnnotSet = 'ohdsi-eu-spc-annotation-set-%s' % annotationSetCntr 
annotationSetCntr += 1
graph.add((poc[currentAnnotSet], RDF.type, oa["DataAnnotation"])) # TODO: find out what is being used for collections in OA
graph.add((poc[currentAnnotSet], oa["annotatedAt"], Literal(datetime.date.today())))
graph.add((poc[currentAnnotSet], oa["annotatedBy"], URIRef(u"http://www.pitt.edu/~rdb20/triads-lab.xml#TRIADS")))

outf = codecs.open(OUTPUT_FILE,"w","utf8")
s = graph.serialize(format="n3",encoding="utf8", errors="replace")
outf.write(s)

# DEBUG
cntr = 0 

inf = open(DATA_FILE, 'r')
buf = inf.read()
inf.close()
lines = buf.split("\n")
it = [unicode(x.strip(),'utf-8', 'replace').split("\t") for x in lines[29:]] # skip header
for elt in it:
    print "%s" % elt
    if elt == [u'']:
        break 

    # if cntr == 20:
    #    break
    cntr += 1
    print cntr
    
    #rxcuiDrug = elt[RxNorm] # There is no RxNorm provided in CTD
    meshDrug = elt[CHEMICAL_ID] # MeSH
    drugLabs = elt[CHEMICAL_NAME]

    # print "WE MADE IT HERE!! ..."

    imedsDrug = None
    if MESH_D_OMOP.has_key(meshDrug):
        imedsDrug = MESH_D_OMOP[meshDrug]
        print "INFO: meshDrug : %s" % meshDrug
    else:
        print "WARNING: skipping meshDrug, no mapping to OMOP : %s" % meshDrug
    #   continue

    # print "WE MADE IT HERE!! ?"
    
    if(imedsDrug != None):
    	rxcuiDrug = None
    	if DRUGS_D_OMOP.has_key(imedsDrug):
    	    rxcuiDrug = DRUGS_D_OMOP[imedsDrug]
    	    print "INFO: imedsDrug : %s" % imedsDrug
    	else:
    	    print "WARNING: skipping imedsDrug, no mapping to RxNorm : %s" % imedsDrug
    	    continue

    # print "WE MADE IT HERE!! ."

    imedsHoi = None
    if MESH_D_OMOP.has_key(elt[DISEASE_ID][5:]):
        imedsHoi = MESH_D_OMOP[elt[DISEASE_ID][5:]]
        print "INFO: meshHoi : %s" % elt[DISEASE_ID][5:]
    else:
        print "WARNING: skipping meshDrug %s + MeSH HOI %s : unable to map HOI to OMOP" % (meshDrug, elt[DISEASE_ID][5:])
        continue

    # print "WE MADE IT HERE!!"

    meddraHoi = None
    if MEDDRA_D_OMOP.has_key(imedsHoi):
        meddraHoi = MEDDRA_D_OMOP[omop]
        print "INFO: imedsHoi : %s" % imedsHoi
    else:
        print "WARNING: skipping imedsHoi %s + meddra HOI %s : unable to map OMOP to meddra HOI" % (imedsHoi, meddraHoi)
    #    continue

MESH_D_OMOP = {}
f = open(MESH_TO_OMOP,"r")
buf = f.read()
f.close()
l = buf.split("\n")
for elt in l[1:]:
    if elt.strip() == "":
        break

    (omop,concept_name,mesh) = [x.strip() for x in elt.split("|")]
    MESH_D_OMOP[mesh] = omop


    ###################################################################
    ### Each annotations holds one target that points to the source
    ### record in DailyMed, and one or more bodies each of which
    ### indicates the MedDRA terms that triggered the result and holds
    ### some metadata
    ###################################################################
    currentAnnotItem = None

    if annotatedCache.has_key(cntr):
        currentAnnotation = annotatedCache[cntr]
        currentAnnotItem = "ohdsi-ctd-annotation-item-%s" % currentAnnotation
    else:
        currentAnnotation = annotationItemCntr
        annotatedCache[cntr] = currentAnnotation
        annotationItemCntr += 1
        
        currentAnnotItem = "ohdsi-ctd-annotation-item-%s" % currentAnnotation

        tplL = []
        #tplL.append((poc[currentAnnotSet], aoOld["item"], poc[currentAnnotItem])) # TODO: find out what is being used for items of collections in OA
        tplL.append((poc[currentAnnotItem], RDF.type, oa["DataAnnotation"]))
        tplL.append((poc[currentAnnotItem], RDF.type, ohdsi["ADRAnnotation"]))
        tplL.append((poc[currentAnnotItem], oa["annotatedAt"], Literal(datetime.date.today())))
        tplL.append((poc[currentAnnotItem], oa["annotatedBy"], URIRef(u"http://www.pitt.edu/~rdb20/triads-lab.xml#TRIADS")))
        tplL.append((poc[currentAnnotItem], oa["motivatedBy"], oa["tagging"]))
        # TODO: add in PROV wasGeneratedBY

        currentAnnotTargetUuid = URIRef(u"urn:uuid:%s" % uuid.uuid4())
        tplL.append((poc[currentAnnotItem], oa["hasTarget"], currentAnnotTargetUuid))
        tplL.append((currentAnnotTargetUuid, RDF.type, oa["SpecificResource"]))
        tplL.append((currentAnnotTargetUuid, oa["hasSource"], URIRef(u"http://ctdbase.org/downloads/#cd")))

        s = ""
        for t in tplL:
            s += unicode.encode(" ".join((t[0].n3(), t[1].n3(), t[2].n3(), u".\n")), 'utf-8', 'replace')
        outf.write(s)
                
    # TODO: CTD data has nothing to use for OA:Selector at this
    # time. Work with UMC to get links to the original SPC documents
    # annotated

    # Specify the bodies of the annotation - for this type each
    # body contains the drug and condition as a semantic tags
    currentAnnotationBody = "ohdsi-ctd-annotation-body-%s" % annotationBodyCntr
    annotationBodyCntr += 1
    
    tplL = []
    tplL.append((poc[currentAnnotItem], oa["hasBody"], poc[currentAnnotationBody]))
    tplL.append((poc[currentAnnotationBody], RDFS.label, Literal(u"Drug-HOI tag for %s-%s" % (imedsDrug, imedsHoi))))
    tplL.append((poc[currentAnnotationBody], RDF.type, ohdsi["adrAnnotationBody"])) # TODO: this is not yet formalized in a public ontology but should be

    tplL.append((poc[currentAnnotationBody], dcterms["description"], Literal(u"Drug-HOI tag for %s - %s" % (elt[CHEMICAL_NAME], elt[DISEASE_NAME]))))
    tplL.append((poc[currentAnnotationBody], ohdsi['ImedsDrug'], ohdsi[imedsDrug]))
#   tplL.append((poc[currentAnnotationBody], ohdsi['RxnormDrug'], rxnorm[rxcuiDrug]))
                        
#   tplL.append((poc[currentAnnotationBody], ohdsi['MeddrraHoi'], meddra[meddraHoi])) # TODO: consider adding the values as a collection
    tplL.append((poc[currentAnnotationBody], ohdsi['ImedsHoi'], ohdsi[imedsHoi])) # TODO: consider adding the values as a collection

    # TODO: Define these predicates - preferrably from an ontology
    tplL.append((poc[currentAnnotationBody], ohdsi['InferenceGeneSymbol'], Literal(elt[INFERENCE_GENE_SYMBOL])))
    tplL.append((poc[currentAnnotationBody], ohdsi['InferenceScore'], Literal(elt[INFERENCE_SCORE])))

    # if len(elt) > COMMENT:
    # tplL.append((poc[currentAnnotationBody], ohdsi['CuratorComment'], Literal(elt[COMMENT])))
    s = ""
    for t in tplL:
        s += unicode.encode(" ".join((t[0].n3(), t[1].n3(), t[2].n3(), u".\n")), 'utf-8', 'replace')

    # print "WE MADE IT HERE!!"

    outf.write(unicode(s,'utf-8', 'replace'))

outf.close

graph.close()