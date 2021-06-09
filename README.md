# gather-pypi-package-info

Just a testing script to gather PyPI package information.

This simple script can be run in OpenShift to gather information from Warehouse JSON API. The information is gathered from `https://pypi.org/pypi/<package-name>/json` endpoint. An example can be data available for package [Flask](https://pypi.org/pypi/Flask/json).

## Deployment

This job can be deployed to OpenShift using:

``oc process -f openshift.yaml | oc apply -f -``

To perform a cleanup of all the objects created:

``oc delete job,is,bc -l app=pypi-gather-package-info``
