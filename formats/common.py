
from synbiohub_adapter.SynBioHubUtil import SD2Constants

"""Some constants to populate samples-schema.json
   compliant outputs
"""
class SampleConstants():

    """Obvious issues with this, welcome something more robust.
    """
    def infer_file_type(file_name):

        if file_name.endswith("fastq.gz"):
            return SampleConstants.F_TYPE_FASTQ
        elif file_name.endswith("zip"):
            return SampleConstants.F_TYPE_ZIP
        elif file_name.endswith("fcs"):
            return SampleConstants.F_TYPE_FCS
        elif file_name.endswith("sraw"):
            return SampleConstants.F_TYPE_SRAW
        elif file_name.endswith("txt"):
            return SampleConstants.F_TYPE_TXT
        elif file_name.endswith("csv"):
            return SampleConstants.F_TYPE_CSV
        elif file_name.endswith("mzML"):
            return SampleConstants.F_TYPE_MZML
        elif file_name.endswith("msf"):
            return SampleConstants.F_TYPE_MSF
        else:
            raise ValueError("Could not parse FT: {}".format(file_name))

    # For circuits
    LOGIC_PREFIX = "http://www.openmath.org/cd/logic1#"

    #experiment
    EXPERIMENT_ID = "experiment_id"
    CHALLENGE_PROBLEM = "challenge_problem"

    CP_NOVEL_CHASSIS = "NOVEL_CHASSIS"
    CP_YEAST_GATES = "YEAST_GATES"

    CP_UNKNOWN = "UNKNOWN"
    CP_REF_UNKNOWN = "Unknown"

    EXPERIMENT_REFERENCE = "experiment_reference"
    EXPERIMENT_REFERENCE_URL = "experiment_reference_url"
    EXPT_DEFAULT_REFERENCE_GINKGO = "NovelChassis-NAND-Gate"

    LAB = "lab"
    LAB_GINKGO = "Ginkgo"
    LAB_TX = "Transcriptic"
    LAB_UWBF = "UW_BIOFAB"

    #samples
    SAMPLES = "samples"
    SAMPLE_ID = "sample_id"
    STRAIN = "strain"
    CONTENTS = "contents"
    REPLICATE = "replicate"
    INOCULATION_DENSITY = "inoculation_density"
    TEMPERATURE = "temperature"
    TIMEPOINT = "timepoint"
    NAME = "name"
    VALUE = "value"
    UNIT = "unit"

    LABEL = "label"
    CIRCUIT = "circuit"
    INPUT_STATE = "input_state"
    SBH_URI = "sbh_uri"
    LAB_ID = "lab_id"
    AGAVE_URI = "agave_uri"

    STANDARD_TYPE = "standard_type"
    STANDARD_FOR = "standard_for"
    STANDARD_FLUORESCEIN = "FLUORESCEIN"

    CONTROL_TYPE = "control_type"
    CONTROL_FOR = "control_for"
    CONTROL_BASELINE_MEDIA_PR = "BASELINE_MEDIA_PR"

    #measurements
    MEASUREMENTS = "measurements"
    FILES = "files"
    FILE_ID = "file_id"
    FILE_LEVEL = "level"
    F_LEVEL_0 = "0"
    F_LEVEL_1 = "1"
    F_LEVEL_2 = "2"
    F_LEVEL_3 = "3"

    MEASUREMENT_TYPE = "measurement_type"
    MEASUREMENT_NAME = "measurement_name"
    SAMPLE_TMT_CHANNEL = "TMT_channel"
    MEASUREMENT_ID = "measurement_id"
    MEASUREMENT_GROUP_ID = "measurement_group_id"
    MT_RNA_SEQ = "RNA_SEQ"
    MT_FLOW = "FLOW"
    MT_PLATE_READER = "PLATE_READER"
    MT_PROTEOMICS = "PROTEOMICS"
    M_NAME = "name"
    M_TYPE = "type"
    M_STATE = "state"
    M_STATE_RAW = "RAW"
    M_STATE_PROCESSED = "PROCESSED"

    F_TYPE_SRAW = "SRAW"
    F_TYPE_FASTQ = "FASTQ"
    F_TYPE_CSV = "CSV"
    F_TYPE_FCS = "FCS"
    F_TYPE_ZIP = "ZIP"
    F_TYPE_TXT = "TXT"
    F_TYPE_MZML = "MZML"
    F_TYPE_MSF = "MSF"

def convert_value_unit(value_unit):
    value_unit_split = value_unit.split(":")
    value = value_unit_split[0]
    if type(value) == int:
        value_unit_split[0] = int(value)
    elif type(value) == float:
        value_unit_split[0] = float(value)
    else:
        value_unit_split[0] = float(value)
    return value_unit_split

def create_media_component(media_name, media_id, lab, sbh_query, value_unit=None):
    m_c_object = {}

    m_c_object[SampleConstants.NAME] = create_mapped_name(media_name, media_id, lab, sbh_query)
    if value_unit:
        value_unit_split = convert_value_unit(value_unit)
        m_c_object[SampleConstants.VALUE] = value_unit_split[0]
        m_c_object[SampleConstants.UNIT] = value_unit_split[1]

    return m_c_object

# cache query lookups
sbh_cache = {}
mapping_failures = {}

def create_mapped_name(name_to_map, id_to_map, lab, sbh_query, strain=False):
    m_n_object = {}

    sbh_lab = None
    if lab == SampleConstants.LAB_GINKGO:
        sbh_lab = SD2Constants.GINKGO
    elif lab == SampleConstants.LAB_TX:
        sbh_lab = SD2Constants.TRANSCRIPTIC
    elif lab == SampleConstants.LAB_UWBF:
        sbh_lab = SD2Constants.BIOFAB
    else:
        raise ValueError("Could not parse lab for SBH lookup: {}".format(lab))

    # SBH expects strings
    if type(id_to_map) == int:
        id_to_map = str(id_to_map)

    if id_to_map in sbh_cache:
        designs = sbh_cache[id_to_map]
    else:
        designs = sbh_query.query_designs_by_lab_ids(sbh_lab, [id_to_map], verbose=True)
        sbh_cache[id_to_map] = designs

    if len(designs) > 0 and id_to_map in designs:
        values = designs[id_to_map]
        if isinstance(values, list):
            # we can only hold a single value here for now, take the first one
            # TODO DR/SBHA team fix this for current cases
            # and we make this throw an error for future runs
            values = values[0]
        # use URI and title from SBH
        sbh_uri = values["identity"]
        m_n_object[SampleConstants.SBH_URI] = sbh_uri
        m_n_object[SampleConstants.LABEL] = values["name"]
        # for strains, we have a SBH URI and can see if there is a circuit
        # associated with this strain
        if strain:
            circuit = query_circuit_from_strain(sbh_uri, sbh_query)
            # e.g. http://www.openmath.org/cd/logic1#nand
            if len(circuit) > 0:
                circuit = circuit[0]["o"]["value"]
                if circuit.startswith(SampleConstants.LOGIC_PREFIX):
                    circuit = circuit.split(SampleConstants.LOGIC_PREFIX)[1].upper()
                    m_n_object[SampleConstants.CIRCUIT] = circuit

                    # grab the circuit's input state
                    input_state = query_input_state_from_strain(sbh_uri, sbh_query)
                    if len(input_state) > 0:
                        input_state = input_state[0]["o"]["value"]
                        #TODO - remove string hacking, better way to encode this in SBH?
                        # e.g. stateful UW strains; UWBF_AND_10
                        if input_state.startswith("UWBF_"):
                            input_state = input_state[-2:]
                            m_n_object[SampleConstants.INPUT_STATE] = input_state
    else:
        # if we do not have a valid mapping, pass through the original lab name
        m_n_object[SampleConstants.LABEL] = name_to_map
        m_n_object[SampleConstants.SBH_URI] = "NO PROGRAM DICTIONARY ENTRY"
        if name_to_map not in mapping_failures:
            mapping_failures[name_to_map] = id_to_map
            with open('create_mapped_name_failures.csv', 'a+') as unmapped:
                unmapped.write('"{}","{}","{}"\n'.format(lab, name_to_map, id_to_map))

    #m_n_object[SampleConstants.AGAVE_URI] =
    m_n_object[SampleConstants.LAB_ID] = namespace_lab_id(id_to_map, lab)
    return m_n_object

# temperature, time, etc.
def create_value_unit(value_unit):
    v_u_object = {}
    value_unit_split = convert_value_unit(value_unit)
    v_u_object[SampleConstants.VALUE] = value_unit_split[0]
    v_u_object[SampleConstants.UNIT] = value_unit_split[1]
    return v_u_object

# Query for a logic circuit (and, or, etc.) for a given strain
def query_circuit_from_strain(strain, sbh_query):

    _id = strain + SampleConstants.CIRCUIT
    if _id in sbh_cache:
        strain_circuit = sbh_cache[_id]
    else:
        # TODO Nic replace this with a real SBHA query
        query = """PREFIX sbol: <http://sbols.org/v2#>
select distinct ?o where {{ <{}> <http://sbols.org/v2#role> ?o }}""".format(strain)

        strain_circuit = sbh_query.fetch_SPARQL(SD2Constants.SD2_SERVER, query)['results']['bindings']
        sbh_cache[_id] = strain_circuit

    return strain_circuit

# Query for an input state for a circuit (00, 01, etc.) for a given strain
def query_input_state_from_strain(strain, sbh_query):

    _id = strain + SampleConstants.INPUT_STATE

    if _id in sbh_cache:
        strain_input_state = sbh_cache[_id]
    else:
        # TODO Nic replace this with a real SBHA query
        query = """
select distinct ?o where {{ <{}> <http://purl.org/dc/terms/title> ?o }}""".format(strain)

        strain_input_state = sbh_query.fetch_SPARQL(SD2Constants.SD2_SERVER, query)['results']['bindings']
        sbh_cache[_id] = strain_input_state

    return strain_input_state

def namespace_sample_id(sample_id, lab):
    '''Prevents collisions amongst lab-specified sample_id'''
    return '.'.join(['sample', lab.lower(), str(sample_id)])

def namespace_measurement_id(measurement_id, lab):
    '''Prevents collisions amongst lab-specified measurement_id'''
    return '.'.join(['measurement', lab.lower(), str(measurement_id)])

def namespace_file_id(file_id, lab):
    '''Prevents collisions amongst lab-specified file_id'''
    return '.'.join(['file', lab.lower(), str(file_id)])

def namespace_lab_id(lab_id, lab):
    '''Prevents collisions amongst lab-specified lab_id'''
    return '.'.join(['name', lab.lower(), str(lab_id)])

def namespace_experiment_id(lab_id, lab):
    '''Prevents collisions amongst lab-specified experiment_id'''
    return '.'.join(['experiment', lab.lower(), str(lab_id)])
