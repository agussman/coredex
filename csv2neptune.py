#!/usr/bin/env python
'''
Load a CSV file into an AWS Neptune instance. Inefficiently and Dangerously.
'''
from __future__  import print_function  # Python 2/3 compatibility
import argparse
import csv

from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.traversal import T

import logging
logging.basicConfig()
LOG = logging.getLogger('csv2neptune')
LOG.setLevel(logging.DEBUG)

def id_transform(original_id):
    return "id_"+original_id

def main():
    # Read the variables
    args = parse_options()
    neptune = args.neptune
    v_file = args.vertices
    e_file = args.edges

    # Connect to Neptune
    neptune_constr = "ws://%s/gremlin" % neptune
    LOG.debug("Connecting to Neptune REST Endpoint %s", neptune)
    graph = Graph()

    g = graph.traversal().withRemote(DriverRemoteConnection(neptune_constr,'g'))

    # Load the nodes / vertices from csv
    with open(v_file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            myid = id_transform(row["~id"])
            print(myid)
            v = g.addV(row["~label"]).property(T.id, myid)
            for key in row:
                if key.startswith('~'):
                    continue
                plabel, ptype = key.split(':')
                v.property(plabel, row[key])
            v.next()

    # Load the edges
    with open(e_file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            edge_id = id_transform(row["~id"])
            from_id = id_transform(row["~from"])
            to_id = id_transform(row["~to"])
            print(edge_id)

            e = g.V(from_id).addE(row["~label"]).to( g.V(to_id) ).property(T.id, edge_id).next()

            for key in row:
                if key.startswith('~'):
                    continue
                plabel, ptype = key.split(':')
                e.property(plabel, row[key])
            e.next()


    print(g.V().limit(2).toList())


def parse_options():
     parser = argparse.ArgumentParser(description='Load CSVs into AWS Neptune')
     parser.add_argument('-n', '--neptune', dest='neptune', action="store", metavar="URI:PORT", required=True)
     parser.add_argument('-v', '--vertices', dest='vertices', action="store", metavar="FILE", required=True)
     parser.add_argument('-e', '--edges', dest='edges', action="store", metavar="FILE", required=True)
     
     return parser.parse_args()

if __name__ == '__main__':
    main()
