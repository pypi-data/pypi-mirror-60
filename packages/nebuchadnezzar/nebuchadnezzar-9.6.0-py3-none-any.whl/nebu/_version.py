
# This file was generated by 'versioneer.py' (0.18) from
# revision-control system data, or from the parent directory name of an
# unpacked source archive. Distribution tarballs contain a pre-generated copy
# of this file.

import json

version_json = '''
{
 "date": "2020-01-22T12:46:25-0600",
 "dirty": false,
 "error": null,
 "full-revisionid": "b31ce4fd6184a124320c1c1102c023b1347db39d",
 "version": "9.6.0"
}
'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)
