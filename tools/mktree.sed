#! /usr/bin/ssed -Rf

s/([^ \t\n\(\)]+)/"\1"/g
s/\)(?!\s*\))/\),/g
s/"([^ "]+)"(?!\))/"\1",/g
s/\(/tree\(/g