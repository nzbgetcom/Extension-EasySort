#!/usr/bin/env python
#
# EasySort post-processing script for NZBGet.
#
# Copyright (C) 2015 Andrey Prygunkov <hugbug@users.sourceforge.net>
# Copyright (C) 2024-2025 Denis <denis@nzbget.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with the program.  If not, see <http://www.gnu.org/licenses/>.
#


import sys
import os
import shutil
import traceback

# Exit codes used by NZBGet
POSTPROCESS_SUCCESS = 93
POSTPROCESS_NONE = 95
POSTPROCESS_ERROR = 94

# Check if the script is called from nzbget 15.0 or later
if not "NZBOP_NZBLOG" in os.environ:
    print("*** NZBGet post-processing script ***")
    print("This script is supposed to be called from nzbget (15.0 or later).")
    sys.exit(POSTPROCESS_ERROR)

# Check if directory still exist (for post-process again)
if not os.path.exists(os.environ["NZBPP_DIRECTORY"]):
    print(
        "[INFO] Destination directory %s doesn't exist, exiting"
        % os.environ["NZBPP_DIRECTORY"]
    )
    sys.exit(POSTPROCESS_NONE)

# Check status for errors
if os.environ["NZBPP_TOTALSTATUS"] != "SUCCESS":
    print(
        '[WARNING] Download of "%s" has failed, exiting' % (os.environ["NZBPP_NZBNAME"])
    )
    sys.exit(POSTPROCESS_NONE)

# Check if all required script config options are present in config file
required_options = (
    "NZBPP_NzbName",
    "NZBPO_DestDir",
    "NZBPO_UseCategoryDir",
    "NZBPO_UseNzbParentDir",
    "NZBPO_Extensions",
    "NZBPO_MinSize",
    "NZBPO_Overwrite",
    "NZBPO_Cleanup",
    "NZBPO_Preview",
    "NZBPO_Verbose",
    "NZBPP_Category",
)
for optname in required_options:
    if not optname.upper() in os.environ:
        print(
            "[ERROR] Option %s is missing in configuration file. Please check script settings"
            % optname[6:]
        )
        sys.exit(POSTPROCESS_ERROR)

# Init script config options
nzb_name = os.environ["NZBPP_NZBNAME"]
download_dir = os.environ["NZBPP_DIRECTORY"]
dest_dir = os.environ["NZBPO_DESTDIR"]
use_category_dir = os.environ["NZBPO_USECATEGORYDIR"] == "yes"
use_nzb_parent_dir = os.environ["NZBPO_USENZBPARENTDIR"] == "yes"
extensions = os.environ["NZBPO_EXTENSIONS"].lower().split(",")
min_size = int(os.environ["NZBPO_MINSIZE"])
min_size <<= 10
overwrite = os.environ["NZBPO_OVERWRITE"] == "yes"
cleanup = os.environ["NZBPO_CLEANUP"] == "yes"
preview = os.environ["NZBPO_PREVIEW"] == "yes"
verbose = os.environ["NZBPO_VERBOSE"] == "yes"
category = os.environ["NZBPP_CATEGORY"]

if dest_dir == "":
    print("[WARNING] Option DestDir cannot be empty, exiting")
    sys.exit(POSTPROCESS_ERROR)

# Relative paths
if not (
    dest_dir[1] == "/"
    or dest_dir[1] == "\\"
    or (len(dest_dir) > 2)
    and dest_dir[2] == ":"
):
    dest_dir = os.path.join(download_dir, dest_dir)

if use_category_dir:
    dest_dir = os.path.join(dest_dir, category)

if use_nzb_parent_dir:
    dest_dir = os.path.join(dest_dir, nzb_name)

dest_dir = os.path.abspath(dest_dir)

if verbose:
    print("Normalized dest directory: %s" % dest_dir)

if preview:
    print("[WARNING] *** PREVIEW MODE ON - NO CHANGES TO FILE SYSTEM ***")

# List of moved files (source path)
moved_src_files = []

# List of moved files (destination path)
moved_dst_files = []

# Separator character used between file name and opening brace
# for duplicate files such as "My Movie (2).mkv"
dupe_separator = " "


def guess_dupe_separator(filename):
    """Find out a char most suitable as dupe_separator"""
    global dupe_separator

    dupe_separator = " "
    fname = os.path.splitext(filename)[0]

    if fname.find(".") > -1:
        dupe_separator = "."
        return

    if fname.find("_") > -1:
        dupe_separator = "_"
        return


def unique_name(new):
    """Adds unique numeric suffix to destination file name to avoid overwriting
    such as "filename.(2).ext", "filename.(3).ext", etc.
    If existing file was created by the script it is renamed to "filename.(1).ext".
    """
    fname, fext = os.path.splitext(new)
    suffix_num = 2
    while True:
        new_name = fname + dupe_separator + "(" + str(suffix_num) + ")" + fext
        if not os.path.exists(new_name) and new_name not in moved_dst_files:
            break
        suffix_num += 1
    return new_name


def optimized_move(old, new):
    try:
        os.rename(old, new)
    except OSError as ex:
        print("[DETAIL] Rename failed ({}), performing copy: {}".format(ex, new))
        shutil.copyfile(old, new)
        os.remove(old)


def rename(old, new):
    """Moves the file to its sorted location.
    It creates any necessary directories to place the new file and moves it.
    """
    if os.path.exists(new) or new in moved_dst_files:
        if overwrite and new not in moved_dst_files:
            os.remove(new)
            optimized_move(old, new)
            print("[INFO] Overwrote: %s" % new)
        else:
            # rename to filename.(2).ext, filename.(3).ext, etc.
            new = unique_name(new)
            rename(old, new)
    else:
        if not preview:
            if not os.path.exists(os.path.dirname(new)):
                os.makedirs(os.path.dirname(new))
            optimized_move(old, new)
        print("[INFO] Moved: %s" % new)
    moved_src_files.append(old)
    moved_dst_files.append(new)
    return new


def cleanup_download_dir():
    if verbose:
        print("Cleanup")

    # Now delete all files with nice logging
    for root, dirs, files in os.walk(download_dir):
        for filename in files:
            path = os.path.join(root, filename)
            if not preview or path not in moved_src_files:
                if not preview:
                    os.remove(path)
                print("[INFO] Deleted: %s" % path)
    if not preview:
        shutil.rmtree(download_dir)
    print("[INFO] Deleted: %s" % download_dir)


def construct_path(filename):
    """Parses the filename and generates new name for renaming"""

    if verbose:
        print("filename: %s" % filename)

    filename = os.path.basename(filename)

    if verbose:
        print("basename: %s" % filename)

    # Find out a char most suitable as dupe_separator
    guess_dupe_separator(filename)

    new_path = os.path.join(dest_dir, filename)

    if verbose:
        print("destination path: %s" % new_path)

    return new_path


# Flag indicating that anything was moved. Cleanup possible.
files_moved = False

# Flag indicating any error. Cleanup is disabled.
errors = False

# Process all the files in download_dir and its subdirectories
move_files = []

for root, dirs, files in os.walk(download_dir):
    for old_filename in files:
        try:
            if verbose:
                print("[INFO] Processing: %s" % old_filename)

            old_path = os.path.join(root, old_filename)

            # Check extension
            if extensions != [""]:
                ext = os.path.splitext(old_filename)[1].lower()
                if ext not in extensions:
                    continue

            # Check minimum file size
            if os.path.getsize(old_path) < min_size:
                print("[INFO] Skipping small: %s" % old_filename)
                continue

            # This is our file, we should process it
            move_files.append(old_path)

        except Exception as e:
            errors = True
            print("[ERROR] Failed: %s" % old_filename)
            print("[ERROR] %s" % e)
            traceback.print_exc()

if verbose:
    print("File list: %s" % move_files)

for old_path in move_files:
    try:
        new_path = construct_path(old_path)

        # Move file
        if new_path:
            rename(old_path, new_path)
            files_moved = True

    except Exception as e:
        errors = True
        print("[ERROR] Failed: %s" % old_filename)
        print("[ERROR] %s" % e)
        traceback.print_exc()

# Inform NZBGet about new destination path
finaldir = ""
uniquedirs = []
for filename in moved_dst_files:
    dir = os.path.dirname(filename)
    if dir not in uniquedirs:
        uniquedirs.append(dir)
        finaldir += "|" if finaldir != "" else ""
        finaldir += dir

if finaldir != "":
    print("[NZB] FINALDIR=%s" % finaldir)

# Cleanup if:
# 1) files were moved AND
# 2) no errors happen
if cleanup and files_moved and not errors:
    cleanup_download_dir()

# Returing status to NZBGet
if errors:
    sys.exit(POSTPROCESS_ERROR)
elif files_moved:
    sys.exit(POSTPROCESS_SUCCESS)
else:
    sys.exit(POSTPROCESS_NONE)
