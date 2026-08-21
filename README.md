## Requirements

- NZBGet v23+ and Python 3.8+
- Legacy NZBGet v22: use v2.0 release

# EasySort
[Post-processing](https://nzbget.com/documentation/post-processing-scripts/) script for [NZBGet](https://nzbget.com).

This script moves files with specified extensions into another directory.

It offers flexible organization options:

- **Flat Mode:** Files are moved into the specified `DestDir` directory.
- **Parent Directory Mode:** Files are moved into the parent directory using `DestDir=..` (flattening).
- **Category Subdirectory Mode:** Files are organized into subdirectories within `DestDir` based on the category using `UseCategoryDir`.
- **NZB Parent Subdirectory Mode:** Files are organized into subdirectories within `DestDir` based on the NZB filename using `UseNzbParentDir`.

You can combine `UseCategoryDir` and `UseNzbParentDir` for further organization.

Additionally, there is an option to delete the source directory with all remaining files.

## Installation

- Download the newest version from [releases page](https://github.com/nzbgetcom/Extension-EasySort/releases).
- Unpack into pp-scripts directory. Your pp-scripts directory now should have folder "EasySort" with "main.py" and "manifest.json";
- Open settings tab in NZBGet web-interface and define settings for EasySort;
- Save changes and restart NZBGet.

## Authors

- Andrey Prygunkov <hugbug@users.sourceforge.net>
- Denis <denis@nzbget.com>

