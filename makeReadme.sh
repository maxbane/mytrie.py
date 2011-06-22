#!/bin/bash
awk '/mytrie.py/,/END MODULE DOC/' mytrie.py > README
