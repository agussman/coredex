#!/usr/bin/env python
""" A command-line utility for dumping the WMATA transportation map as .csv file
    suitable for loading into Neptune.

    Sign up for an API key at https://developer.wmata.com/docs/services/
"""
import logging
import argparse
import json
import glob
import collections
import csv
import requests

# Custom modules
#import util.colorized_console_logging

APP_NAME = 'wmata2csv'

logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.DEBUG)

loggingFileHandler = logging.FileHandler(APP_NAME+'.log', mode='w')
loggingFileHandler.setLevel(logging.DEBUG)

loggingFormatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s (%(filename)s:%(lineno)d )')
loggingFileHandler.setFormatter(loggingFormatter)

logger.addHandler(loggingFileHandler)

def main():
    logger.debug('Starting...')

    args = load_cmdline_args()

    url = 'http://api.wmata.com/Rail.svc/json/jLines'
    headers = {'api_key': args.api_key}

    r = requests.get(url, headers=headers)

    # Get the lines
    lines = {}
    for l in r.json()['Lines']:
        print(l["DisplayName"])
        lines[l["LineCode"]] = {
            "id": l["LineCode"],
            "name": l["DisplayName"],
            "color": l["DisplayName"].lower(),
            "StartStationCode": l["StartStationCode"],
            "EndStationCode": l["EndStationCode"]
        }

    #print(lines)


    # Get the Stations
    url = 'http://api.wmata.com/Rail.svc/json/jStations'
    r = requests.get(url, headers=headers)

    stations = {}
    code_to_station = {}
    for s in r.json()['Stations']:
        # One station can have multiple track Codes, so we need the dict lookup
        code_to_station[s['Code']] = s['Name']

        #print(s)

        # This doesn't do what I want; lots of stations have multiple lines
        # Set the color
        # if s["LineCode2"] == None:
        #     color = "purple"
        # else:
        #     color = lines[s["LineCode1"]]["color"]
        if s["StationTogether1"] is not None and s["StationTogether1"]:
            #print("|"+s["StationTogether1"]+"|")
            color = "purple"
        else:
            color = lines[s["LineCode1"]]["color"]



        # Station names are the only way to id stations?
        # note that the same station shows up multiple times but we're just clobbering it and loosing Code/StationTogether1 info
        stations[s['Name']] = {
            "~id": s['Name'],
            "~label": "STATION",
            "name:string": s['Name'],
            "lat:double": s['Lat'],
            "lon:double": s['Lon'],
            #"color:string": lines[s["LineCode1"]]["color"]
            "color:string": color
        }


    # Write stations to disk
    out_file_name = "data/station-nodes.csv"
    out_fh = None
    try:
        out_fh = open(out_file_name, mode='wb')
    except IOError as io_err:
        err_msg = "Unable to write to file (%s). %s" % (out_file_name, io_err)
        logger.error(err_msg)
        print(err_msg)
        exit(1)

    sorted_headers=["~id", "~label", "name:string", "lat:double", "lon:double", "color:string"]
    writer = csv.DictWriter(out_fh, sorted_headers, restval='', extrasaction='ignore', delimiter=',')
    writer.writeheader()
    for station in stations.values():
        writer.writerow(station)


    # Get the track segments
    segments = {}
    for line in lines.values():
        # For each line, pull down the full path
        payload = {
            "FromStationCode": line["StartStationCode"],
            "ToStationCode": line["EndStationCode"]
        }


        url = 'https://api.wmata.com/Rail.svc/json/jPath'
        r = requests.get(url, headers=headers, params=payload)

        paths = r.json()["Path"]
        prev_code = line["StartStationCode"]
        for p in paths[1:]:
            id = "%s_%s" % (prev_code, p["StationCode"])
            #print(s)
            segments[id] = {
                "~id": id,
                "~from": code_to_station[prev_code],
                "~to": code_to_station[p["StationCode"]],
                "~label": "SEGMENT",
                "distance:int": p["DistanceToPrev"],
                "linecode:string": p["LineCode"],
                "color:string": lines[p["LineCode"]]["color"]
            }

            # Create the same track in the opposite direction
            id = "%s_%s" % (p["StationCode"], prev_code)
            #print(s)
            segments[id] = {
                "~id": id,
                "~from": code_to_station[p["StationCode"]],
                "~to": code_to_station[prev_code],
                "~label": "SEGMENT",
                "distance:int": p["DistanceToPrev"],
                "linecode:string": p["LineCode"],
                "color:string": lines[p["LineCode"]]["color"]
            }

            prev_code = p["StationCode"]


    # Write track segments to disk
    out_file_name = "data/station-edges.csv"
    out_fh = None
    try:
        out_fh = open(out_file_name, mode='wb')
    except IOError as io_err:
        err_msg = "Unable to write to file (%s). %s" % (out_file_name, io_err)
        logger.error(err_msg)
        print(err_msg)
        exit(1)

    sorted_headers=["~id", "~from", "~to", "~label", "distance:int", "color:string"]
    writer = csv.DictWriter(out_fh, sorted_headers, restval='', extrasaction='ignore', delimiter=',')
    writer.writeheader()
    for segment in segments.values():
        writer.writerow(segment)




    # # Confirm we can write the output file before proceeding with more expensive operations like
    # # iterating over several input files...

    #
    # in_files = glob.glob(args.inFiles)
    #
    # # Go through ALL of the JSON files and extract headers (and only headers) from each one. At the
    # # end of this loop we'll be left with a "master" set of headers which covers all possible fields
    # # from all of the JSON files. This is important because we'll be exporting ALL of the JSON files
    # # to a single CSV file; the headers for that file need to cover all possible fields.
    # csv_header_set = set([])
    # counter = 1
    # logger.info("Collecting headers from all files...")
    # for input_filepath in in_files:
    #
    #     # Respect the --limit parameter if specified by user
    #     if counter > args.limit:
    #         break
    #
    #     #logger.debug("Collecting headers from %s" % input_filepath)
    #
    #     try:
    #         json_input_fh = open(input_filepath, mode='r')
    #
    #         # This dictionary may contain other dictionaries (aka "deep")
    #         deep_data_dict = json.load(json_input_fh, encoding=args.inFileEncoding)
    #         json_input_fh.close()
    #
    #         # "Flatten" any child dicts such that we are left with a dictionary whose values will
    #         # never be dictionaries (i.e., no dicts within dicts).
    #         shallow_data_dict = flatten_dict(deep_data_dict)
    #
    #         csv_header_set.update( shallow_data_dict.keys() )
    #
    #     except ValueError as value_err:
    #         err_msg = "Ignoring %s; unable to parse JSON (%s)" % (input_filepath, value_err)
    #         logger.error(err_msg)
    #         print err_msg
    #
    #     except IOError as io_err:
    #         err_msg = "Ignoring %s; unable to open the file (%s)" % (input_filepath, io_err)
    #         logger.error(err_msg)
    #         print err_msg
    #
    #     counter += 1
    #
    #
    # sorted_headers = sorted(list(csv_header_set))
    #
    # # restval parameter specifies the value to be written if the dictionary is missing a key in
    # # fieldnames. extrasaction parameter indicates what action to take if the dictionary passed to
    # # the writerow() method contains a key not found in fieldnames
    # writer = csv.DictWriter(out_fh, sorted_headers, restval='', extrasaction='ignore', delimiter=args.delimiter)
    #
    # logger.debug("Headers: %s" % json.dumps(sorted_headers))
    # logger.info("Writing headers to %s..." % out_file_name)
    # writer.writeheader()
    #
    # # Go through all the JSON files again, but this time output each one to the CSV file.
    # counter = 1
    # for input_filepath in in_files:
    #
    #     # Respect the --limit parameter if specified by user
    #     if counter > args.limit:
    #         break
    #
    #     #logger.debug("Converting %s to CSV" % input_filepath)
    #
    #     try:
    #         json_input_fh = open(input_filepath, mode='r')
    #
    #         # This dictionary may contain other dictionaries (aka "deep")
    #         deep_data_dict = json.load(json_input_fh, encoding=args.inFileEncoding)
    #         json_input_fh.close()
    #
    #         # "Flatten" any child dicts such that we are left with a dictionary whose values will
    #         # never be dictionaries (i.e., no dicts within dicts).
    #         shallow_data_dict = flatten_dict(deep_data_dict)
    #
    #         writer.writerow(shallow_data_dict)
    #
    #     except ValueError as value_err:
    #         err_msg = "Ignoring %s; unable to parse JSON (%s)" % (input_filepath, value_err)
    #         logger.error(err_msg)
    #         print err_msg
    #
    #     except IOError as io_err:
    #         err_msg = "Ignoring %s; unable to open the file (%s)" % (input_filepath, io_err)
    #         logger.error(err_msg)
    #         print err_msg
    #
    #     counter += 1


def flatten_dict(d, parent_key=''):
    """ Due credit to Baby Mouth Holloway for the original version of this function (which was mostly
     just modified to support lists).
    """
    colname_val_tuple_list = []

    for current_key, current_value in d.items():

        # Create a key (i.e., CSV column name). If a parent key was passed in use that as the base.
        colname = "%s.%s" % (parent_key, current_key) if parent_key else current_key

        # If the current value is a dictionary...
        if isinstance(current_value, collections.MutableMapping):

            # ...flatten that dict and convert it to a list of key/value tuples
            flattened_dict_tuple_list = flatten_dict(current_value, colname).items()

            # ...add each of those key/value pairs to the list
            colname_val_tuple_list.extend( flattened_dict_tuple_list )

        # If the current value is a list...
        elif isinstance(current_value, list):

            # ...flatten all items in the list and add the resulting key/value pairs
            flattened_list_tuples = flatten_list(current_value, colname).items()
            colname_val_tuple_list.extend( flattened_list_tuples )

        else:

            # If the value is a unicode string, we need to UTF-8 encode it
            if isinstance(current_value, unicode):
                current_value = current_value.encode('utf8', 'ignore')

            # Add the key/value pair
            colname_val_tuple_list.append( (colname, current_value) )

    # Convert all the key/value pairs (tuples) into a dictionary
    return dict(colname_val_tuple_list)


def flatten_list(the_list, parent_key=''):
    colname_val_tuple_list = []

    # For each item in the list, either append that item as a colname/value pair or flatten the
    # item (i.e., it's a dict) and add those key/value pairs.
    item_counter = 0
    for item in the_list:
        colname = "%s.%s" % (parent_key, item_counter)

        # If the current value is a dictionary...
        if isinstance(item, collections.MutableMapping):

            flattened_item_tuple_list = flatten_dict(item, colname).items()
            colname_val_tuple_list.extend( flattened_item_tuple_list )

        # If the current value is a list...
        elif isinstance(item, list):

            # ...flatten all items in the list and add the resulting key/value pairs
            flattened_list_tuples = flatten_list(item, colname).items()
            colname_val_tuple_list.extend( flattened_list_tuples )

        else:

            # If the value is a unicode string, we need to UTF-8 encode it
            if isinstance(item, unicode):
                item = item.encode('utf8', 'ignore')
                colname_val_tuple_list.append( (colname, item) )

            else:

                # Add the key/value pair
                colname_val_tuple_list.append( (colname, item) )


        item_counter += 1

    # Convert all the key/value pairs (tuples) into a dictionary
    return dict(colname_val_tuple_list)



def load_cmdline_args():
    parser = argparse.ArgumentParser(description="A command-line utility for dumping the WMATA transportation network as CSV")
    #parser.add_argument('--inFiles', nargs='?', required=True, help='Path to input file(s)')
    #parser.add_argument('--inFileEncoding', nargs='?', default="utf-8", help='Encoding for input files. Defaults to UTF-8')
    #parser.add_argument('--outFile', default="out.csv", help='Output CSV')
    #parser.add_argument('--limit', type=int, default=float('inf'), nargs='?', help='Limits the number of input files that are processed')
    parser.add_argument('--verbose', nargs='?', default=False, help='Displays verbose logging to console')
    #parser.add_argument('--delimiter', default=',', help='Character to use as delimiter in output file (default comma)')

    parser.add_argument('-a', '--api_key', dest='api_key', action="store", metavar="API_KEY", required=True)

    args = parser.parse_args()

    # Verbose flag means showing the logger output in the console
    if args.verbose != False:
        loggingConsoleHandler = util.colorized_console_logging.ColorizingStreamHandler()
        loggingConsoleHandler.setLevel(logging.DEBUG)
        loggingConsoleHandler.setFormatter(loggingFormatter)
        logger.addHandler(loggingConsoleHandler)

    return args

if __name__ == '__main__':
    main()
