#!/bin/sh

dir=$(dirname "$0")
repo=$(cd $dir && git rev-parse --show-toplevel)
src="${repo}/IPTables-Guide" 

flake8 $src

if [[ "$?" -ne 0 ]]; then
  echo "flake8 failed"
  exit 1
else
  echo "flake8 passed"
fi

mypy --strict $src > /dev/null

if [[ "$?" -ne 0 ]]; then
  echo "mypy failed"
  exit 1
else
  echo "mypy passed"
fi
