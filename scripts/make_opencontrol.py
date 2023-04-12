#!/usr/bin/env python3

from settings import *
from utils import *

def generate_open_control_file(oc_skel, srvc_nm):
    """Return a simulated open-control object generated from service name"""
    oc_skel.update({'name': srvc_nm}) if 'name' in oc_skel else oc_skel.setdefault('name', srvc_nm)
    # TODO: Generate more content for OpenControl Component
    return oc_skel


if __name__ == "__main__":

    print("running")
    print(f"SERVICES_FILE: {SERVICES_FILE}")

    # read OpenControl skeleton
    with open(os.path.join("input", OC_SKELETON_FILE), 'r') as f:
        os_skel = rtyaml.load(f)

    # read services
    services = open(os.path.join("input", SERVICES_FILE)).read().splitlines()

    # create output dir
    outputdir_oc = os.path.join(OUTPUTDIR, "opencontrol")
    ensure_dir(outputdir_oc)

    # generate OpenControl artifacts
    for srvc_nm in services:
        oc_obj = generate_open_control_file(os_skel, srvc_nm)
        filedir = outputdir_oc
        filename = f"{slugify(oc_obj.get('name', 'error'))}.yaml"
        filepath = os.path.join(filedir, filename)
        print(f"write OpenControl file {filepath}")
        with open(filepath, "w") as f:
            f.write(rtyaml.dump(oc_obj))
