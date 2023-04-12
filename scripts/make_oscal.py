#!/usr/bin/env python3

from settings import *
from utils import *
from utilities import *
import rtyaml
import json
import os
import glob
import uuid
import datetime
from collections import defaultdict
from itertools import groupby
from natsort import natsorted
from dataclasses import dataclass, field

# Dataclasses to re-create relevant GovReady-Q models

def get_datetime():
    return datetime.datetime.now()

def empty_list():
    return []


@dataclass
class Element:
    """Class simulating a GovReady-Q Element (Component)"""

    name: str
    created: datetime.datetime = datetime.datetime.now()
    updated: datetime.datetime = datetime.datetime.now()
    # created: datetime.datetime(2022, 10, 30, 19, 14, 16, 735990, tzinfo=<UTC>),
    # updated: datetime.datetime(2022, 10, 30, 19, 14, 16, 735998, tzinfo=<UTC>),
    full_name: str = ""
    description: str = ""
    element_type: str = ""
    oscal_version: str = "1.0.0"
    uuid: str = str(uuid.uuid4())
    component_type: str = 'software'
    component_state: str = 'operational'
    tags: list = field(default_factory=empty_list)


@dataclass
class Organization:
    """Class simulating a GovReady-Q Organization"""

    name: str = "main"
    slug: str = "main"


@dataclass
class Statement:
    """Class simulating a GovReady-Q Statement"""

    sid: str
    sid_class: str
    source: str
    pid: str
    body: str
    statement_type: str = "CONTROL_IMPLEMENTATION_PROTOTYPE"
    remarks: str = ""
    status: str = ""
    version: str = ""
    # created = models.DateTimeField(auto_now_add=True, db_index=True)
    # updated = models.DateTimeField(auto_now=True, db_index=True)
    uuid: str = str(uuid.uuid4())


# Methods to convert OpenControl content to OSCAL content via GovReady-Q models

def convert_oc_satisfies_to_smt_list(oc_satisfies):
    """Return an array of statement objects given an OpenControl satisfies list"""

    # OpenControl lists implementations statements as items in the `satisfies` list.
    smts = []
    for ctl_item in oc_satisfies:
        # print(ctl_item)
        for narr_item in ctl_item.get("narrative", []):
            try:
                oscal_ctl_id = oscalize_control_id(ctl_item.get("control_key", None))
            except:
                # TODO: add log, warning to user in terminal
                print(f"[ERROR]: Catalog id {ctl_item.get('control_key', None)} could not be oscalized")
                oscal_ctl_id = None
            smt = Statement(sid=oscal_ctl_id,
                            sid_class=ctl_item.get("standard_key", None),
                            source=ctl_item.get("source", None),
                            pid=None,
                            body=None,
                            statement_type="CONTROL_IMPLEMENTATION_PROTOTYPE",
                            remarks=None,
                            status=ctl_item.get("implementation_status", None),
                            #  covered_by=ctl_item.get("covered_by", []),
                            #  security_control_type=ctl_item.get("security_control_type", "")
                            )
            smt.pid = narr_item.get("key", None)
            smt.body = narr_item.get("text", None)
            smts.append(smt)
    return smts


# generate OSCAL statements using GovReady-Q's OSCALComponentSerializer
class ComponentSerializer(object):

    def __init__(self, element, impl_smts):
        self.element = element
        self.impl_smts = impl_smts


class OSCALComponentSerializer(ComponentSerializer):

    @staticmethod
    def statement_id_from_control(control_id, part_id):
        # Checking for a case where the control was provided like ac-2.3 which already has its part included.
        if part_id:
            if part_id not in control_id:
                return f"{control_id}.{part_id}"

        return f"{control_id}"

    def generate_source(self, src_str):
        """Return a valid catalog source given string"""
        # DEFAULT_SOURCE = "NIST_SP-800-53_rev5"
        DEFAULT_SOURCE = "Electronic Version of NIST SP 800-53 Rev 5 Controls and SP 800-53A Rev 5 Assessment Procedures"
        if not src_str:
            return DEFAULT_SOURCE
        # TODO: Handle other cases
        source = src_str
        return source

    def as_json(self):
        # Build OSCAL
        # Example: https://github.com/usnistgov/OSCAL/blob/master/src/content/ssp-example/json/example-component.json
        comp_uuid = str(self.element.uuid)
        control_implementations = []
        props = []

        # orgs
        org = Organization()
        orgs = [org]
        # orgs = list(Organization.objects.all())  # TODO: orgs need uuids, not sure which orgs to use for a component

        parties = [{"uuid": str(uuid.uuid4()), "type": "organization", "name": org.name} for org in orgs]
        responsible_roles = [{
            "role-id": "supplier",  # TODO: Not sure what this refers to
            "party-uuids": [str(party.get("uuid")) for party in parties]

        }]
        of = {
            "component-definition": {
                "uuid": str(uuid.uuid4()),
                "metadata": {
                    "title": "{}".format(self.element.name),
                    "last-modified": self.element.updated.replace(microsecond=0).isoformat(),
                    "version": self.element.updated.replace(microsecond=0).isoformat(),
                    "oscal-version": self.element.oscal_version,
                    "parties": parties
                },
                "components": [
                    {
                        "uuid": comp_uuid,
                        "type": self.element.component_type.lower() if self.element.component_type is not None else "software",
                        "title": self.element.full_name or self.element.name,
                        "description": self.element.description,
                        "responsible-roles": responsible_roles,  # TODO: gathering party-uuids, just filling for now
                        "props": props,
                        "control-implementations": control_implementations
                    }
                ]
            },
        }

        # Add component's tags if they exist
        # if self.element.tags.exists():
        #     props.extend([{"name": "tag", "ns": "https://govready.com/ns/oscal", "value": tag.label} for tag in self.element.tags.all()])

        # Remove 'metadata.props' key if no metadata.props exist
        if len(props) == 0:
            of['component-definition']['metadata'].pop('props', None)

        # create requirements and organize by source (sid_class)

        by_class = defaultdict(list)

        # work:
        # group stmts by control-id
        # emit an requirement for the control-id
        # iterate over each group
        # emit a statement for each member of the group
        # notes:
        # - OSCAL implemented_requirements and control_implementations need UUIDs
        #   which we don't have in the db, so we construct them.

        # print("self.impl_smts:\n", self.impl_smts)

        for control_id, group in groupby(natsorted(self.impl_smts, key=lambda ismt: ismt.sid),
                                         lambda ismt: ismt.sid):

            for smt in group:
                statement_id = self.statement_id_from_control(control_id, smt.pid)
                statement_req = {
                    "uuid": str(smt.uuid),
                    "description": smt.body,
                    "control-id": statement_id,
                }
                # key-value by sid a.k.a control id for each requirement
                if statement_req not in by_class[smt.sid]:
                    by_class[smt.sid].append(statement_req)

        for sid_class, requirements in by_class.items():
            control_implementation = {
                "uuid": str(uuid.uuid4()),  # TODO: Not sure if this should implemented or just generated here.
                "source": self.generate_source(smt.sid_class if smt.sid_class else None),
                "description": f"This is a partial implementation of the {sid_class} catalog, focusing on the control enhancement {requirements[0].get('control-id')}.",
                "implemented-requirements": [req for req in requirements]
            }
            control_implementations.append(control_implementation)
        # Remove 'control-implementations' key if no implementations exist
        if len(control_implementations) == 0:
            of['component-definition']['components'][0].pop('control-implementations', None)

        oscal_string = json.dumps(of, sort_keys=False, indent=2)
        return oscal_string


def generate_oscal_from_opencontrol(oc_obj):
    """Generate OSCAL from OpenControl object"""

    # set name
    component_name = oc_obj.get("name", "missing name")
    component = Element(name=component_name)
    component.full_name = component.name

    # prepare statements
    smts = convert_oc_satisfies_to_smt_list(oc_obj.get('satisfies', []))
    # generate OSCAL using OSCALComponentSerializer
    oscal_cmpt = OSCALComponentSerializer(component, smts)
    # print("oscal_cmpt.as_json\n", oscal_cmpt.as_json())
    return oscal_cmpt.as_json()

def find_occ_files(start_dir, file_extension=".yaml"):
    file_paths = []

    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file.endswith(file_extension):
                print(f'[INFO] Found OpenControl component .yaml file "{os.path.join(root, file)}" ')
                file_path = os.path.join(root, file)
                file_paths.append(file_path)

    return file_paths


if __name__ == "__main__":

    print("running")

    # create output dir
    outputdir_oc = os.path.join(INPUTDIR)
    outputdir_oscal = os.path.join(OUTPUTDIR)
    ensure_dir(outputdir_oscal)
    # Walk directory to find open control yaml files
    start_dir = os.path.join(INPUTDIR)
    ensure_dir(start_dir)
    component_files = find_occ_files(start_dir, ".yaml")
    print(f'[INFO] Found {len(component_files)} component .yaml files')

    # Loop to convert each OpenControl file to OSCAL file
    # for each open-control file, generate an OSCAL file
    # for file in glob.glob(os.path.join(outputdir_oc, "*.yaml")):
    for file in component_files:
        print(f"[INFO] Reading Open Control file {file}")
        with open(file) as f:
            oc_obj = rtyaml.load(f)
        # generate OSCAL from OpenControl
        oscal_obj = json.loads(generate_oscal_from_opencontrol(oc_obj))
        # determine OSCAL file name
        component_name = oc_obj.get("name", "missing name")
        filename_oscal = f"{slugify(component_name)}.json"
        filepath_oscal = os.path.join(outputdir_oscal, filename_oscal)
        # write OSCAL file
        with open(filepath_oscal, "w") as f:
            print(f"[INFO] Created OSCAL file {filepath_oscal}")
            json.dump(oscal_obj, f, ensure_ascii=False, indent=4)
