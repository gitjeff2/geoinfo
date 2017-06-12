# GEOINFO

## Introduction 

The purpose of *geoinfo* is to analyze GEOS CVT archives and generate an easy to read report.

This code is in a very early state. The reporting mechanism works well and works as expected but there isn't a single class or object to be found in this code. With time, that's going to change.

## Project Goal

To create reliable library for handling CVT containers and their payloads. Ultimately, this should see several applications:

1. Extract meta data information reporting application, much as exists now but in fully OOP code.
2. File format translation filters from Commodore GEOS formats to their modern Free/Open Source equivalents.
3. Ideally, support for the Apple 2gs version of GEOS files.
4. The possibility to expand to other legacy formats.
5. While useful, a lot of existing documentation on legacy formats are fragmentary and incomplete. For this project the documentation is as important as the code.

### Requirements and Dependencies

There are no special module dependencies at this time. ***Python 3.6 is required*** as *geoinfo* uses [PEP 515 Underscores in Numeric Literals](https://www.python.org/dev/peps/pep-0515/). It's primarily developed on a Raspberry Pi running [Raspbian](https://www.raspbian.org/).

### What is CVT Archive?

A CVT archive is a container that holds a single GEOS file. The archive contains a header with file system meta data, any resource forks the file needs, along with the file data proper. This allows GEOS files to be transmitted over a network or stored on a non-native GEOS file system without loss or damage that would otherwise occur.

### Why are CVT Files Needed

GEOS is an operating system for the Commodore and Apple 128k line of 8-bit computers. By "operating system" I mean almost everything that implies in the modern sense: a full kernel, drivers, a standard library of functions, and a graphical windowing system, etc. Even telecommunication was possible via a terminal program. That said, it lacks a TCP/IP stack and has a single tasking OS and thus lacks a task scheduler.

GEOS had it's own file system, which deployed in parallel to the C64's own native file system. It did this through file and resource forks in a manner similar to early Macintosh file systems, most notably [MFS](https://en.wikipedia.org/wiki/Macintosh_File_System). The design decision to use resource forks gave GEOS a lot of flexibility to include date and time stamps, icon data, etc. all not supported by the C64's native [CBM DOS](https://en.wikipedia.org/wiki/Commodore_DOS). Ingeniously, this was done in a way that was functionally invisible to native CMD devices, so native C64 applications and data could be stored on a GEOS formatted volume without much hassle. That said, all of this flexibility came at a cost.

Transmitting GEOS files over a telecommunications network of any kind just wasn't possible. Why? Because, every file in GEOS contains both a data fork and a resource fork. The *resource fork* portion of every file never made the trip, producing a corrupt file on the receiving end 100% of the time.

Hence, the need for a CVT container format which encapsulated three important bits of information that would otherwise be lost:

1. A file header with the GEOS file name, time stamp, etc.
2. Resource data such as icon and custom menu strings.
3. The VLIR or SEQ file layout table. GEOS files aren't always linear in their layout.

## Usage

```
$ python3 geoinfo.py [FILE].cvt

```

### Understanding the Output

CONTAINER TYPE: This indicates whether or not the CVT file was created by Blaster's Convert, far and away the most common CVT utility for GEOS. CVT files created by other utilities are listed as "Unknown."

VERSION: The CVT container version string, 2.5 is the most common but others are possible.

FORMAT: This will either read PRG or SEQ. If the CVT file is moved to a Commodore file system this is the file type it will report when a directory listing is called.

CONTENTS: GEOS files have one one two possible payloads: a GEOS SEQ or GEOS VLIR.

FILE NAME: This is the native GEOS file name stored in the header of the CVT file and should not be confused with the name of the CVT file as it appears on a modern file system. GEOS file names can be upwards of 16 characters long. Filenames are encoded in ASCII and only use the lower 0x0&ndash;0x7f range.

FILE SIGNATURE: This is the "magic string" that associates file with their applications, much akin to the "magic numbers" in modern computing.

FILE CLASS: There are 16 possible file classes in GEOS. This is how GEOS internally distinguishes a driver from an application data file, etc.

AUTHOR: This field may or may not be present and contains attribution information for the file. If no author data is found "n/a" is displayed.

LAST MODIFIED: This contains the date and time stamp of the CVT's last modification. GEOS file system time stamps are granular to the minute, not second. (This is strange because internally the C64 could track time in 1/50th of a second increments called 'Jiffies' though it lacked a battery-backed real-time clock.) Unlike modern file systems, file creation times are not stored. Years are stored in 2 digit form, so '87 refers to 1987. The year 1986 is assumed to be the epoch for Y2K purposes as this is the release year of GEOS, thus dates of '17 will treated as 2017.

SIZE: This is the file size in bytes. Most files are only a handful of kilobytes. The theoretical maximum of a GEOS VLIR file is just shy of 8 MB. As such, bytes seemed the most reasonable unit to return.

INFOBOX: This is up to 96-bytes (characters) of arbitrary text that can be inserted into the header of any file typically used for a short reminder as to its contents. 

#### Limitations 

1. Currently, *geoinfo* only supports CVT files that intended for the Commodore line of 8-bit computers. CVT files intended for the Apple 2/2gs GEOS exist, but aren't supported. 
2. The C128 40/80 column display flag is not yet decoded along with certain other flags.
3. Right now, *geoinfo* primarily decodes portions of the CVT header, it is not yet capable of interpreting the VLIR index or decoding the actual file data blocks.

## Related Technical Documents 

* [*GEOS Convert Utility File Structure*](http://www.filegate.net/cbm/g-tech/cvtformt.txt) author unknown.
* [*ConVerT Containers*](http://unusedino.de/ec64/technical/formats/cvt.html) by Joe Forster/[STA](http://sta.c64.org/) author unknown.
* [*Apple GEOS Convert Format*](https://github.com/cc65/wiki/wiki/Apple-GEOS-Convert-Format)
* [*GEOS VLIR*] v1.4 by Paul David Doherty *et al*.
* [*VLIR File Support*](https://www.landley.net/history/mirror/8bits/geos/docs/vlir.txt) author unknown.
* [*VLIR File Structure*](https://www.landley.net/history/mirror/8bits/geos/docs/vlirfile.txt) author unknown.
* [*GEOwrite v2.0/v2.1 File Format*](https://www.landley.net/history/mirror/8bits/geos/docs/writefile.txt) author unknown.
* [*Text and Fonts*](https://www.landley.net/history/mirror/8bits/geos/docs/text.txt) author unknown.
* [*cc65 GEOSLib docs*](http://cc65.github.io/doc/geos.html) by Maciej Witkowiak.
