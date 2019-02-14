#!/usr/bin/env python
'''
Load a CSV file into a Neo4j Database. Inefficiently and Dangerously.
'''
from __future__  import print_function  # Python 2/3 compatibility
import argparse
import csv

from neo4j import GraphDatabase

import logging
logging.basicConfig()
LOG = logging.getLogger('csv2neo4j')
LOG.setLevel(logging.DEBUG)

def id_transform(original_id):
    '''
    This is here for legacy reasons.
    :param original_id:
    :return: modified version of the id to make it looks "stringy" to javascript
    '''
    return "id_"+original_id

def main():
    # Read the variables
    args = parse_options()
    neo4j = args.neo4j
    v_file = args.vertices
    e_file = args.edges

    # Connect to Neo4j
    neo4j_constr = "bolt://%s" % neo4j
    username = args.username
    password = args.password
    LOG.debug("Connecting to neo4j REST Endpoint %s", neo4j)
    
    graphDB_Driver  = GraphDatabase.driver(neo4j_constr, auth=(username, password))

    with graphDB_Driver.session() as graphDB_Session:

        # Load the nodes / vertices from csv
        with open(v_file) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                # Note that we are transforming ids because of a bug in GraphExp
                myid = id_transform(row["~id"])
                print(myid)

                cqlCreateNode = "CREATE (n:Station {{id: \"{}\", name: \"{}\", color:\"{}\"}})".format(myid, row["name:string"], row["color:string"])
                print(cqlCreateNode)
                graphDB_Session.run(cqlCreateNode)

    #             v = g.addV(row["~label"]).property(T.id, myid)
    #             for key in row:
    #                 if key.startswith('~'):
    #                     continue
    #                 plabel, ptype = key.split(':')
    #                 v.property(plabel, row[key])
    #             v.next()

        # Load the edges
        with open(e_file) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                # Note that we are transforming ids because of a bug in GraphExp
                edge_id = id_transform(row["~id"])
                from_id = id_transform(row["~from"])
                to_id = id_transform(row["~to"])
                print(edge_id)

                cqlCreateEdge = "MATCH (a:Station), (b:Station) WHERE a.id = \"{}\" AND b.id = \"{}\" CREATE (a)-[r:SEGMENT]->(b)".format(from_id, to_id)
                print(cqlCreateEdge)
                graphDB_Session.run(cqlCreateEdge)

        #         e = g.V(from_id).addE(row["~label"]).to( g.V(to_id) ).property(T.id, edge_id)

        #         for key in row:
        #             if key.startswith('~'):
        #                 continue
        #             plabel, ptype = key.split(':')
        #             e.property(plabel, row[key])
        #         e.next()


    # print("Vertices: %s" % g.V().count().next())
    # print("Edges: %s" % g.E().count().next())


def parse_options():
     parser = argparse.ArgumentParser(description='Load CSVs into Neo4j')
     parser.add_argument('-n', '--neo4j', dest='neo4j', action="store", metavar="URI:PORT", required=True)
     parser.add_argument('-u', '--username', dest='username', action="store", metavar="STRING", required=True)
     parser.add_argument('-p', '--password', dest='password', action="store", metavar="STIRNG", required=True)
     parser.add_argument('-v', '--vertices', dest='vertices', action="store", metavar="FILE", required=True)
     parser.add_argument('-e', '--edges', dest='edges', action="store", metavar="FILE", required=True)
     
     return parser.parse_args()

if __name__ == '__main__':
    main()
