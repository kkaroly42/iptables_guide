## Running tests

0. Set the `IPTABLES_GUIDE` variable to the project's root dir
   ``export =IPTABLES_GUIDE`pwd` ``
1. Run
```sh
python -m unittest discover -s $IPTABLES_GUIDE/tests -p "*_test.py"
```