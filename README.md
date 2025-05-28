## NZBGet Versions

- stable v23 [v3.1](https://github.com/nzbgetcom/Extension-EasySort/releases/tag/v3.1)
- legacy v22 [v2.0](https://github.com/nzbgetcom/Extension-EasySort/releases/tag/v2.0)

> **Note:** This script is compatible with python 3.8.x and above.
If you need support for Python 2.x versions then you can get legacy version [here](https://forum.nzbget.net/viewtopic.php?f=8&t=2163&p=23026&hilit=easysort#p23026).

## EasySort

This script moves files with specified extensions into another directory.

It offers flexible organization options:

 - Flat Mode:** Files are moved into the specified `DestDir` directory.
 - Parent Directory Mode:** Files are moved into the parent directory using `DestDir=..` (flattening).
 - Category Subdirectory Mode:** Files are organized into subdirectories within `DestDir` based on the category using `UseCategoryDir`.
 - NZB Parent Subdirectory Mode:** Files are organized into subdirectories within `DestDir` based on the NZB filename using `UseNzbParentDir`

You can combine `UseCategoryDir` and `UseNzbParentDir` for further organization.

Additionally, there is an option to delete the source directory with all remaining files.

## Authors:
 - Andrey Prygunkov <hugbug@users.sourceforge.net>
 - Denis <denis@nzbget.com>
