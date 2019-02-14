# Neo4j

Working on a MAC. I ran into issues with the Desktop App being glitched out and not rendering correctly.

Instead downloaded the "Community Edition" from https://neo4j.com/download-thanks/?edition=community&release=3.5.3&flavour=unix

Default login is username 'neo4j' and password 'neo4j'


```
~ $ mkdir neo4j
~ $ cd neo4j
neo4j $ tar xvzf ~/Downloads/neo4j-community-3.5.3-unix.tar.gz
neo4j $ cd neo4j-community-3.5.3/
neo4j-community-3.5.3 $ NEO4J_HOME=$PWD
```

coredex $ mkvirtualenv neo4j
(neo4j) coredex $ pip install neo4j


Refactoring the existing script:
`(neo4j) coredex $ cp csv2neptune.py csv2neo4j.py`

Run it as:
`(neo4j) coredex $ python csv2neo4j.py -n localhost:7687 -u neo4j -p <PASSWORD> -v ./data/station-nodes.csv -e ./data/station-edges.csv`


A couple of notes:
 * Have to have a relationship type
 * Don't see how to get property-based colors



References
 * https://pythontic.com/database/neo4j/create%20nodes%20and%20relationships
 * https://neo4j.com/docs/cypher-manual/current/clauses/create/





