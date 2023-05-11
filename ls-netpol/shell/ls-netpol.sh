#!/bin/env bash
set -euo pipefail

for ns in $(oc get ns --selector zone=dmz,'!maistra.io/member-of' -o custom-columns=NAME:.metadata.name --no-headers)
do
 oc get netpol --no-headers -n "$ns" | awk -v ns=$ns '{print ns "\t" $1}'
done
