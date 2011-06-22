#!/bin/bash
awk '/mytrie.py/,/END MODULE DOC/' mytrie.py | head -n-1 > README.md && 
    cat VERSIONS.md >> README.md
