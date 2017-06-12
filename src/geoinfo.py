# This program opens a Variable Length Index Record (VLIR) files 
# in CVT containers and displays the metadata.

# TODO
# * Word wrap --help

import sys 
import os

ver = "0.02a"

def noFile():
    notice = """geoinfo.py: missing file name.
Usage: python3 geoinfo.py [FILENAME].CVT

Try `geoinfo.py --help` for more information.
"""
    return notice


def helpMessage():
    message = """Usage: python3 geoinfo.py [FILE].cvt

Extract general metadata from GEOS Convert (CVT) containers and display it in an easy to read report. 

The GEOS operating system originated on the Commodore 64 and makes frequent use of resource forks in ways very reminiscent of the early Macintosh file system MFS. Because of this, GEOS data transmitted or stored outside of a GEOS file system needs to be stored in a container format that preserved the resource data stored in the local file system; hence the CVT container.

CONTAINER TYPE: This indicates whether or not the CVT file was created by Blaster's Convert, far and away the most common CVT utility for GEOS. CVT files created by other utilities are listed as "Unknown."

VERSION: The CVT container version string, 2.5 is the most common but others are possible.

FORMAT: This will either read PRG or SEQ. If the CVT file is moved to a Commodore file system this is the file type it will report when a directory listing is called.

CONTENTS: GEOS files have one one two possible payloads: a GEOS SEQ or GEOS VLIR.

FILE NAME: This is the native GEOS file name stored in the header of the CVT file and should not be confused with the name of the CVT file as it appears on a modern file system. GEOS file names can be upwards of 16 characters long. Filenames are encoded in ASCII and only use the lower 0x0 - 0x7f range.

FILE SIGNATURE: This is the "magic string" that associates file with their applications, much akin to the "magic numbers" in modern computing.

FILE CLASS: There are 16 possible file classes in GEOS. This is how GEOS internally distinguishes a driver from an application data file, etc.

AUTHOR: This field may or may not be present and contains attribution information for the file. If no author data is found "n/a" is displayed.

LAST MODIFIED: This contains the date and time stamp of the CVT's last modification. GEOS file system time stamps are granular to the minute, not second. (This is strange because internally the C64 could track time in 1/50th of a second increments called 'Jiffies' though it lacked a battery-backed real-time clock.) Unlike modern file systems, file creation times are not stored. Years are stored in 2 digit form, so '87 refers to 1987. The year 1986 is assumed to be the epoch for Y2K purposes as this is the release year of GEOS, thus dates of '17 will treated as 2017.

SIZE: This is the file size in bytes. Most files are only a handful of kilobytes. The theoretical maximum of a GEOS VLIR file is just shy of 8 MB. As such, bytes seemed the most reasonable unit to return.

INFOBOX: This is up to 96-bytes (characters) of arbitrary text that can be inserted into the header of any file typically used for a short reminder as to its contents. 

LIMITATIONS: (1) geoinfo only supports CVT files that intended for the Commodore line of 8-bit computers. CVT files intended for the Apple 2/2gs GEOS exist, but aren't supported. (2) The C128 40/80 column display flag is not yet decoded.
"""
    return message


if len(sys.argv) == 1:
    print(noFile())
    sys.exit(-1)
elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
    print(helpMessage()) 
    sys.exit(-1)
elif sys.argv[1] == "--version" or sys.argv[1] == "-V":
    print("geoinfo.py version", ver) 
    sys.exit(-1)

inputFile = sys.argv[1]


with open(inputFile, 'rb') as f:
    filecontents = f.read()

bytelist = []


def sanityFileSize():
    # Sanity Check: A file 256 bytes or smaller can't possibly be valid.
    # Max partition size for CBM DOS is 16MB.

    # Get file size in BYTES
    fsize = os.path.getsize(inputFile)

    # PEP 515, Python 3.6
    if fsize <= 256 or fsize >= 8_388_608:
        print(inputFile, "is the wrong size to be a valid GEOS CVT file.")
        sys.exit(-1)
    else: pass

sanityFileSize()

# Convert each byte to hex and add it to a list.
for i in filecontents:
    i = hex(i)
    bytelist.append(i)


def hexToASCII(x):
    # Convert a single byte of hex to ASCII and return it as a 1-byte string.
    # GEOS internally real ASCII, not PETSCII.

    character = chr(int(x,16))
    return character


def metaGetSEQorPRG():
    ext = ""
    for i in bytelist[0x1e:0x21]: # [30:33]
        ext += hexToASCII(i)

    return ext


def metaVLIRorSEQ():
    # Check to determine if the file structure is GEOS VLIR or GEOS SEQ.
    # This is not the same as having a SEQ formatted CVT file.

    if bytelist[0x15] == '0x0': # [21]
        result = "GEOS SEQ"

    elif bytelist[0x15] == '0x1': # [21]
        result = "GEOS VLIR"

    else:
         result = "NOT GEOS"

    return result


def metaGetFileSize(size,si):
    # Return a human readable file size.

    size = len(size)

    if si == "b" or si == "B":
        result = size
        result = '{:,}'.format(result)
        si = "bytes"

    if si == "kb" or si == "KB":
        result = size / 1024
        result = '{:,0.2f}'.format(result)
        si = "kB"

    if si == "mb" or si == "MB":
        result = size / 1048576
        result = '{:,0.2f}'.format(result)
        si = "MB"

    return result, si

def metaGetFileName():
    # Extract the original GEOS filename from a file. 
    # This may differ from the file's name on the local file system.
    # The CVT header also contains file size data, I might use that in the 
    # future instead.

    filename = ""

    for i in bytelist[0x03:0x13]: # [3:19]
        filename += hexToASCII(i)

    # Clean up any leading or trailing whitespace issues.
    filename = filename.strip()

    return filename


def metaGetFileSig():
    # Return the file signature; GEOS calls this the class.

    accumulator = []
    result = ""
    n = 329

    while bytelist[n] != '0x0':
        accumulator.append(bytelist[n])
        n +=1

    for i in accumulator:
        result += hexToASCII(i)

    result = " ".join(result.split())

    return result

    # Clean up any leading or trailing whitespace issues.
    filetype = filetype.strip()

    return filetype


def metaGetFileType():
    ftype = bytelist[0x16] # [22]
    result = ""

    if ftype == '0x0':
        result = "non-GEOS"
    
    elif ftype == '0x1':
        result = "BASIC"

    elif ftype == '0x2':
        result = "Assembler"

    elif ftype == '0x3':
        result = "Data File"

    elif ftype == '0x4':
        result = "System File"

    elif ftype == '0x5':
        result = "Desk Accessory"

    elif ftype == '0x6':
        result = "Application"

    elif ftype == '0x7':
        result = "Application Data"

    elif ftype == '0x8':
        result = "Font"

    elif ftype == '0x9':
        result = "Print Driver"

    elif ftype == '0xa':
        result = "Input Driver"

    elif ftype == '0xb':
        result = "Disk Driver"

    elif ftype == '0xc':
        result = "System Boot File"

    elif ftype == '0xd':
        result = "Temporary File"

    elif ftype == '0xe':
        result = "Auto Exec"

    elif ftype == '0xf':
        result = "Commodore 128 Input Driver"

    else:
        result = "UNKNOWN"

    return result


def metaGetAuthor():

    accumulator = []
    n = 0x15d # 349 
    result = ""

    while bytelist[n] != '0x0':
        accumulator.append(bytelist[n])
        n += 1

    for i in accumulator:
        result += hexToASCII(i)

    result = " ".join(result.split())

    if result == "" or result == " ":
        return "n/a"

    else:
        return result

def metaGetDateTime():
    # This function returns the GEOS file system time stamp of the file.
    # This is, of course, different from the local file system time stamp
    # of the CVT file being analyzed.

    # Dates and times are all two digit standard hex and not BCD.
    # Hours are in 24 hour time not 12 hour time.

    # Get Date Stamp and convert to base 10 from base 16.
    year = int(bytelist[0x17],16)    # [23]
    month = int(bytelist[0x18],16)   # [24]
    day = int(bytelist[0x19],16)     # [25]

    # Get Time Stamp and convert to base 10 from base 16.
    hour = int(bytelist[0x1a],16)    # [26]
    minute = int(bytelist[0x1b],16)  # [27]

    # Unfortunately, time stamps have minute-level granularity and seconds 
    # are not captured. So, zero seconds are supplied.
    second = 0 

    # Convert the two digit year to a 4 digit year using the release year 
    # of GEOS as the epoch for Y2K purposes.
    if year > 85:
        year = year + 1900
    else:
    # This works until 2086-01-01.
        year = year + 2000

    # Zero pad the remaining two digit fields.
    month = '{:02d}'.format(month)
    day = '{:02d}'.format(day)

    hour = '{:02d}'.format(hour)
    minute = '{:02d}'.format(minute)
    second = '{:02d}'.format(second)

    return year, month, day, hour, minute, second


def littlEndianBCDtoInt(x):
    # This function is not currently used. It won't see use until 
    # geoCalc support is added.

    # This function accepts little endian BCD and returns a big endian integer.
    # This function isn't used yet, pending geoCalc support.
    
    # GEOS uses a multiple variants of Binary Coded Decimal depending upon
    # the operation. One of them is little-endian, least bit & byte first.
    # This is surely a speed optimization: the MOS 6502/6510 is little-endian.

    # Convert the 8-bit byte into two strings, each containing a 4-bit
    # nibble.
    byte = format(x, '08b')
    leastSignificantNibble = byte[0:4]
    mostSignificantNibble = byte[5:8]

    # Directly convert each nibble from base 2 to base 10
    # No lookup table required.
    mostSignificantInt = int(leastSignificantNibble,2)
    leastSignificantInt = int(mostSignificantNibble,2)

    # Make integer big endian.
    result =  mostSignificantInt * 10 + leastSignificantInt 

    return result


def infoboxPresent():
    # True/False test to see if an infobox is present in a GEOS file.

    # Grab the indicator bit and decode to an base 10 int.
    infoboxIndicatorBit = int(bytelist[0x19c],16) # [412]

    # Check for contents.
    if infoboxIndicatorBit != 0x0:
        return True 
    else:
        return False 


def metaGetInfoboxContents():
    # This function returns the actual contents of an GEOS file's infobox.

    # Set the counter to the first byte of the infobox: 0x19c
    n = 0x19c #412 

    # Accumulate the byte list
    accumulator = []
    result = ""

    if infoboxPresent() == True:

    # Read each byte of the infobox until the end of field marker is reached.
        while bytelist[n] != '0x0':
            accumulator.append(bytelist[n])
            n += 1

        for i in accumulator:
            result += hexToASCII(i)

        result = " ".join(result.split())

        return result


def identifyContainerFormat():
    # Get the Convert File string to minimially confirm it's an actual
    # GEOS Convert file.

    magicList = bytelist[0x9e:0xb1] # [158:177]
    magicString = ""

    for i in magicList:
        magicString += hexToASCII(i)

    if magicString == "BLASTER'S CONVERTER":
        return "Blaster's Convert"
    else:
        return "Non-Blaster's Convert" 


def identifyContainerVersion():
    # Get the Convert container file version

    verList = bytelist[0xb2:0xb6] # [178:182]
    verString = ""

    for i in verList:
        verString += hexToASCII(i)

    verString = " ".join(verString.split())

    if verString[0] != "V":
        return "Unknown"
    else: 
        return verString[1:]


def checkIfCVT():
    ext = inputFile[-4:]
    ext = ext.lower()

    if ext == ".cvt":
        return True
    else: return False


def report():

    print("Container Type: ",identifyContainerFormat(),sep="")
    print("       Version: ",identifyContainerVersion(),sep="")
    print("        Format: ",metaGetSEQorPRG(),sep="")
    print("       Payload: ",metaVLIRorSEQ(),sep="")
    print("")
    print("     File Name: ",metaGetFileName(),sep="")
    print("    File Class: ",metaGetFileSig(),sep="")
    print("     File Type: ",metaGetFileType(),sep="")
    print("        Author: ",metaGetAuthor(),sep="")

    YYYY, MM, DD, hh, mm, ss = metaGetDateTime()
    print(" Last Modified: ",YYYY,"-",MM,"-",DD," at ",hh,":",mm,":",ss,sep="")
    fsize, si = metaGetFileSize(bytelist, "b")
    print("          Size:",fsize,si)

    if infoboxPresent() == True:
        print("       Infobox: ", metaGetInfoboxContents(),sep="")
    else:
        print("       Infobox: ")


def main():
    report()

if __name__ == "__main__":
    main()
