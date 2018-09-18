#!/usr/bin/python
import json
import sys
import os
from jsonschema import validate
from jsonschema import ValidationError
import six
from jq import jq
# Hack hack
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from common import SampleConstants
from common import namespace_sample_id, namespace_file_id, namespace_measurement_id, namespace_experiment_id, create_media_component, create_value_unit, create_mapped_name
from synbiohub_adapter.query_synbiohub import *
from synbiohub_adapter.SynBioHubUtil import *
from sbol import *

def extend_biofab_filename(file_name, plan_id, generated_by):
    # Add context to the filename while we have enough information to
    # generate it
    gen_id = None
    if 'operation_id' in generated_by:
        gen_id = 'op_' + generated_by['operation_id']
    elif 'job_id' in generated_by:
        gen_id = 'job_' + generated_by['job_id']
    else:
        gen_id = 'unknown'
    return '/'.join([str(plan_id), gen_id, file_name])


def convert_biofab(schema_file, input_file, verbose=True, output=True, output_file=None, config={}, enforce_validation=True):

    # for SBH Librarian Mapping
    sbh_query = SynBioHubQuery(SD2Constants.SD2_SERVER)

    schema = json.load(open(schema_file))
    biofab_doc = json.load(open(input_file))

    output_doc = {}

    lab = SampleConstants.LAB_UWBF

    original_experiment_id = biofab_doc["plan_id"]
    output_doc[SampleConstants.EXPERIMENT_ID] = namespace_experiment_id(biofab_doc["plan_id"], lab)
    output_doc[SampleConstants.CHALLENGE_PROBLEM] = biofab_doc.get("attributes", {}).get("challenge_problem", "UNKNOWN")
    output_doc[SampleConstants.EXPERIMENT_REFERENCE] = biofab_doc.get(
        "attributes", {}).get("experiment_reference", "Unknown")

    output_doc[SampleConstants.LAB] = biofab_doc.get("attributes", {}).get("lab", lab)
    output_doc[SampleConstants.SAMPLES] = []

    for biofab_sample in biofab_doc["files"]:
        sample_doc = {}
        file_source = biofab_sample["sources"][0]
        # sample_doc[SampleConstants.SAMPLE_ID] = file_source
        sample_doc[SampleConstants.SAMPLE_ID] = namespace_sample_id(file_source, lab)

        #print(biofab_sample)
        #print(file_source)
        item = jq(".items[] | select(.item_id==\"" + file_source + "\")").transform(biofab_doc)

        # plate this source is a part of?
        #print(item)
        type_of_media_attr = "type_of_media"
        part_of_attr = "part_of"
        attributes_attr = "attributes"
        plate = None
        found_plate = False
        part_of = None
        if part_of_attr not in item:
            #print(item)
            if attributes_attr in item and type_of_media_attr in item[attributes_attr]:
                # use ourself instead of doing part_of
                plate = item
                found_plate = True
                part_of = file_source
            else:
                print("TODO, parse: {}".format(file_source))
                continue
        else:
            part_of = item[part_of_attr]
            plate = jq(".items[] | select(.item_id==\"" + part_of + "\")").transform(biofab_doc)

        #print(plate)
        reagents = []

        plate_source_lookup = None
        plate_source = None
        # one additional lookup
        if found_plate:
            plate_source = plate["sources"][0]
            plate_source_lookup = plate
        else:
            plate_source = plate["sources"][0]
            plate_source_lookup = jq(".items[] | select(.item_id==\"" + plate_source + "\")").transform(biofab_doc)

        #print(plate_source_lookup)
        media_name = plate_source_lookup[attributes_attr][type_of_media_attr]

        # need to follow *another* source chain to find the media_id
        if "sources" not in item:
            # case for old files that do not have this.
            reagents.append(create_media_component(media_name, media_name, lab, sbh_query))
        else:
            media_source_ = item["sources"][0]
            media_source_lookup = jq(".items[] | select(.item_id==\"" + media_source_ + "\")").transform(biofab_doc)
            #print(media_source_lookup)
            if attributes_attr in media_source_lookup and "media" in media_source_lookup[attributes_attr]:
                if "sample_id" in media_source_lookup[attributes_attr]["media"]:
                    media_id = media_source_lookup[attributes_attr]["media"]["sample_id"]
                    #print(media_id)
                    reagents.append(create_media_component(media_name, media_id, lab, sbh_query))
                else:
                    raise ValueError("No media id? {}".format(media_source_lookup))
            else:
                # no ID, pass name through
                reagents.append(create_media_component(media_name, media_name, lab, sbh_query))

        temperature = plate_source_lookup["attributes"]["growth_temperature"]
        sample_doc[SampleConstants.TEMPERATURE] = create_value_unit(str(temperature) + ":celsius")

        sample_doc[SampleConstants.CONTENTS] = reagents

        # optical_density
        if attributes_attr in media_source_lookup and "od600" in media_source_lookup[attributes_attr]:
            od = media_source_lookup[attributes_attr]["od600"]
            sample_doc[SampleConstants.INOCULATION_DENSITY] = create_value_unit(od + ":od600")

        # could use ID
        #print(item)
        sample_attr = "sample"
        if sample_attr in item:
            sample_id = item[sample_attr]["sample_id"]
            strain = item[sample_attr]["sample_name"]
            sample_doc[SampleConstants.STRAIN] = create_mapped_name(strain, sample_id, lab, sbh_query, strain=True)

        # TODO replicate
        # Compute this? Biofab knows the number of replicates, but does not individually tag...
        # "name": "Biological Replicates",
        #  "field_value_id": "451711",
        #  "value": "6"

        # skip controls for now
        # code from Ginkgo doc...
        """
        control_for_prop = "control_for_samples"
        sbh_uri_prop = "SD2_SBH_URI"
        if control_for_prop in biofab_sample:
            control_for_val = biofab_sample[control_for_prop]

            #int -> str conversion
            if isinstance(control_for_val, list):
                if type(control_for_val[0]) == int:
                    control_for_val = [str(n) for n in control_for_val]

            if sbh_uri_prop in props:
                sbh_uri_val = props[sbh_uri_prop]
                if "fluorescein_control" in sbh_uri_val:
                    sample_doc[SampleConstants.STANDARD_TYPE] = SampleConstants.STANDARD_FLUORESCEIN
                    sample_doc[SampleConstants.STANDARD_FOR] = control_for_val
                else:
                    print("Unknown control for sample: {}".format(sample_doc[SampleConstants.SAMPLE_ID]))
            else:
                print("Unknown control for sample: {}".format(sample_doc[SampleConstants.SAMPLE_ID]))
        """
        measurement_doc = {}
        #print(part_of):
        try:
            time_val = jq(".operations[] | select(.inputs[].item_id ==\"" + plate_source + "\").inputs[] | select (.name == \"Timepoint (hr)\").value").transform(biofab_doc)
            measurement_doc[SampleConstants.TIMEPOINT] = create_value_unit(time_val + ":hour")
        except StopIteration:
            print("Warning: Could not find matching time value for {}".format(part_of))

        measurement_doc[SampleConstants.FILES] = []

        assay_type = biofab_sample["type"]
        if assay_type == "FCS":
            measurement_type = SampleConstants.MT_FLOW
        elif assay_type == "CSV":
            measurement_type = SampleConstants.MT_PLATE_READER
        else:
            raise ValueError("Could not parse MT: {}".format(assay_type))

        measurement_doc[SampleConstants.MEASUREMENT_TYPE] = measurement_type

        # operation id aggregates across files for a single measurement, e.g.
        """
        "operation_id": "92240",
        "operation_type": {
        "operation_type_id": "415",
        "category": "Flow Cytometry",
        "name": "Flow Cytometry 96 well"
        },
        """
        # generate a measurement id unique to this sample
        # Biofab does not have additional measurements per file, can fix to 1
        measurement_doc[SampleConstants.MEASUREMENT_ID] = namespace_measurement_id(
            ".".join([sample_doc[SampleConstants.SAMPLE_ID], "1"]), output_doc[SampleConstants.LAB])

        # record a measurement grouping id to find other linked samples and files
        measurement_doc[SampleConstants.MEASUREMENT_GROUP_ID] = namespace_measurement_id(
            biofab_sample["generated_by"]["operation_id"], output_doc[SampleConstants.LAB])

        # TODO
        #measurement_doc[SampleConstants.MEASUREMENT_NAME] = measurement_props["measurement_name"]

        if config.get('extend', False):
            file_name = extend_biofab_filename(
                biofab_sample['filename'], original_experiment_id, biofab_sample['generated_by'])
        else:
            file_name = biofab_sample["filename"]

        file_id = biofab_sample.get('file_id', None)
        if file_id is not None:
            file_id = namespace_file_id(file_id, lab)
        file_type = SampleConstants.infer_file_type(file_name)
        measurement_doc[SampleConstants.FILES].append(
                            { SampleConstants.M_NAME : file_name, \
                            SampleConstants.M_TYPE : file_type, \
                            SampleConstants.M_STATE : SampleConstants.M_STATE_RAW,
                            SampleConstants.FILE_LEVEL: SampleConstants.F_LEVEL_0,
                            SampleConstants.FILE_ID: file_id})

        if len(measurement_doc[SampleConstants.FILES]) == 0:
            print("Warning, measurement contains no files, skipping {}".format(measurement_key))
        else:
            if SampleConstants.MEASUREMENTS not in sample_doc:
                sample_doc[SampleConstants.MEASUREMENTS] = []
            sample_doc[SampleConstants.MEASUREMENTS].append(measurement_doc)

        output_doc[SampleConstants.SAMPLES].append(sample_doc)

    try:
        validate(output_doc, schema)
        #if verbose:
            #print(json.dumps(output_doc, indent=4))
        if output is True or output_file is not None:
            if output_file is None:
                path = os.path.join("output/biofab", os.path.basename(input_file))
            else:
                path = output_file
            with open(path, 'w') as outfile:
                json.dump(output_doc, outfile, indent=4)
        return True
    except ValidationError as err:
        if enforce_validation:
            raise ValidationError("Schema Validation Error", err)
        else:
            if verbose:
                print("Schema Validation Error: {0}\n".format(err))
            return False
        return False

if __name__ == "__main__":
    path = sys.argv[2]
    if os.path.isdir(path):
        for f in os.listdir(path):
            file_path = os.path.join(path, f)
            print(file_path)
            if file_path.endswith(".js") or file_path.endswith(".json"):
                convert_biofab(sys.argv[1], file_path)
            else:
                print("Skipping {}".format(file_path))
    else:
        convert_biofab(sys.argv[1], sys.argv[2])
