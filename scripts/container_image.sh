#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$DIR/common.sh"
read_reactor_rc
echo -n "${CONTAINER_IMAGE}"
