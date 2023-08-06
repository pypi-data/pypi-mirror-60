# Script Name: darfortie.py
# Author: Ken Galle
# License: GPLv3
# Description: returns a dictionary of values to be used as parameters in the dar command:

#import logging
import glob
import os.path
from operator import itemgetter

# returns previous filename
def get_previous_file(dest_path_and_base_name, text_sort):
    #log = logging.getLogger('darfortie_previous_file')

    retval = None
    #log.info("going into glob.glob = " + dest_path_and_base_name + "*.1.dar")
    filelist = glob.glob(dest_path_and_base_name + "*.1.dar")
    if len(filelist) > 0:
        filedata = []
        for onefile in filelist:
            # get the last modified datetime for each file
            filedata.append( (onefile, os.path.getmtime(onefile)) )

        # sort the list by the date
        if text_sort:
            sorted_list = sorted(filedata, key=itemgetter(0), reverse=True)
        else:
            sorted_list = sorted(filedata, key=itemgetter(1), reverse=True)

#        for myfile in sorted_list:
#            log.info("filelist item = " + myfile[0])

        retval = sorted_list[0][0]
#        log.info("chosen item = " + retval)
    return retval

def remove_slice_number_and_extension(full_previous_file):
    retval = None
    # I know the slice number will be 1 and the extension will be 'dar'
    index = full_previous_file.rfind(".1.dar", 0)
    if index > 0:
        retval = full_previous_file[0:index]
    return retval

def get_previous_file_date_time(dest_basename, previous_file):
    #log = logging.getLogger('darfortie_previous_file')

    #log.info("dest_basename = " + dest_basename)
    #log.info("previous_file = " + previous_file)
    # dest_basename: 'asus_root_system_daily'
    # previous_file:  'destination/asus_root_system_daily_20131227_0347UTC.1.dar'
    retval = None
    base_position = previous_file.rfind(dest_basename)
    if base_position is not -1:
        # calculate index of just past the base name
        date_start_index = base_position + len(dest_basename) + 1
        # the date/time will always be 16 characters long
        date_end_index = date_start_index + 16
        # slice off the date portion of the previous file
        previous_date = previous_file[date_start_index:date_end_index]
        #log.info("previous_date = " + previous_date)
        retval = previous_date
    return retval
