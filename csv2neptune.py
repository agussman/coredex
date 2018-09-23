#!/usr/bin/env python
'''
Load a CSV file into an AWS Neptune instance. Inefficiently.
'''
from __future__  import print_function  # Python 2/3 compatibility
# import fileinput
# import glob
import argparse
import csv
# import os
# from os.path import basename
#
# from bs4 import BeautifulSoup


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

def main():
    # Read the variables
    args = parse_options()
    neptune = args.neptune
    v_file = args.vertices

    # Connect to Neptune
    neptune_constr = "ws://%s/gremlin" % neptune
    LOG.debug("Connecting to Neptune REST Endpoint %s", neptune)
    graph = Graph()

    g = graph.traversal().withRemote(DriverRemoteConnection(neptune_constr,'g'))

    # Load the nodes / vertices from csv
    #csvreader = csv.reader(fileinput.input(), delimiter=',', quotechar='"')
    with open(v_file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            myid = "id_"+row["~id"]
            print(row["~id"])
            v = g.addV(row["~label"]).property(T.id, myid)
            #v.property("foo", "bar")
            #v.property("ack", "syn")
            for key in row:
                if key.startswith('~'):
                    continue
                v.property(key, "yes")
            v.next()


    print(g.V().limit(2).toList())


def parse_options():
     parser = argparse.ArgumentParser(description='Load CSVs into AWS Neptune')
     #parser.add_argument('crds', metavar='N', type=int, nargs='+', help="description") # grab the arguments as a list, they need to be ints
     #parser.add_argument('-f', '--files', dest='input_glob', action="store", metavar="GLOB", required=True)
     #parser.add_argument('-o', '--out_dir', dest='out_dir', action="store", metavar="DIR", required=True)
     parser.add_argument('-n', '--neptune', dest='neptune', action="store", metavar="URI:PORT", required=True)
     parser.add_argument('-v', '--vertices', dest='vertices', action="store", metavar="FILE", required=True)
     
     return parser.parse_args()

if __name__ == '__main__':
    main()
