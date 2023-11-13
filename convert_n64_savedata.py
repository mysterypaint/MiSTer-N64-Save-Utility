import os, sys, argparse, shutil
from enum import Enum
from pathlib import Path

SaveState = Enum('SaveState', ['NO_INJECTION', 'HAS_INJECTION', 'INVALID'])

def dumpGBSave(savePathN64, savePathGBDump):
    try:
        # Write the contents of the N64 Save into the GB Save and format it accordingly
        saveFileGB = open(savePathGBDump, "wb")
        with open(savePathN64, 'br') as f:
            f.seek(0x00020000)
            data = f.read(4)
            for offset in range(0x00020000, 0x00027FFF, 0x4):
                saveFileGB.write(data[::-1])
                data = f.read(4)
        saveFileGB.close()
    except FileNotFoundError:
        print("File not found.")
    except OSError:
        print("OS error occurred.")

def checkSaveSize(savePathN64):
    try:
        file_size = os.path.getsize(savePathN64)

        if (file_size == 0x40000):
            return SaveState.HAS_INJECTION
        elif (file_size > 0x40000):
            print(f"Invalid save filesize: {file_size}")
            return SaveState.INVALID
        return SaveState.NO_INJECTION
    except FileNotFoundError:
        print("File not found.")
        return SaveState.INVALID
    except OSError:
        print("OS error occurred.")
        return SaveState.INVALID

def injectGBSave(savePathN64, savePathGB, saveSize):
    # Back up the N64 save before we inject anything
    savePathN64Bak = os.path.join(os.path.dirname(savePathN64), Path(savePathN64).stem + "_pre-injection.sav")
    
    # Back up the N64 save
    shutil.copyfile(savePathN64, savePathN64Bak)

    # Pad the end of the file with zeros if we never injected a GB Save into this N64 Save
    if (saveSize == SaveState.NO_INJECTION):
        with open(savePathN64, 'a+') as f:
            size = os.stat(savePathN64).st_size
            f.write('\0' * (2*0x20000 - size))
            f.close()
            print("file padded!")

    # Inject the GB Save data into the N64 Save File, pre-formatting it too
    saveFileN64Bak = open(savePathN64Bak, "rb")
    saveFileN64 = open(savePathN64, "wb")
    data = saveFileN64Bak.read(0x20000)
    saveFileN64.write(data)
    gbChunkSize = 0
    with open(savePathGB, 'br') as f:
        gbChunkSize = os.stat(savePathGB).st_size
        data = f.read(4)
        for offset in range(0x00020000, 0x00027FFF, 0x4):
            saveFileN64.write(data[::-1])
            data = f.read(4)
        
        # Pad the rest of our 0x40000-sized Output N64 Save file with 00s
        saveFileN64.write(b'\0' * (0x40000 - saveFileN64.tell()))
        f.close()
    saveFileN64.close()

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle

savePathN64 = ''
savePathGB = ''
savePathGBDump = ''
dumpGBEnabled = False
injectGBEnabled = False

parser = argparse.ArgumentParser("convert_tpak_data.py")
parser.add_argument("-n64", help="Input & Output N64 Save Path", nargs='?', default="N64.sav")
parser.add_argument("-gb", help="Input GB Save Path", nargs='?', default="GB_in.sav")
parser.add_argument('-d', help="Flag: The GB save should be dumped from the N64 save", action='store_true', default=False)
parser.add_argument('-i', help="Flag: The GB save should be injected into the N64 save", action='store_true', default=False)
parser.add_argument("-exp", help="Path to export GB Save Dump from the N64 Save", nargs='?', default="GB_out.sav")

if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    exit

args = parser.parse_args()

if (args.n64 == "N64.sav" or args.n64 == None or args.n64 == ""):
    savePathN64 = "N64.sav"
else:
    savePathN64 = args.n64
if (args.gb == "GB_in.sav" or args.gb == None or args.gb == ""):
    savePathGB = "GB_in.sav"
else:
    savePathGB = args.gb
if (args.exp == "GB_out.sav" or args.exp == None or args.exp == ""):
    savePathGBDump = "GB_out.sav"
else:
    savePathGBDump = args.exp

dumpGBEnabled = args.d
injectGBEnabled = args.i

saveSize = checkSaveSize(savePathN64)

match saveSize:
    case SaveState.NO_INJECTION:
        if (dumpGBEnabled):
            print("There is no GB Save to dump!")
        if (injectGBEnabled):
            print("Injecting GB Save into: " + savePathN64)
            injectGBSave(savePathN64, savePathGB, saveSize)
        exit
    case SaveState.HAS_INJECTION:
        if (dumpGBEnabled):
            dumpGBSave(savePathN64, savePathGBDump)
        if (injectGBEnabled):
            print("There is already an injection! Overwriting: " + savePathN64)
            injectGBSave(savePathN64, savePathGB, saveSize)
        exit
    case SaveState.INVALID:
        print("Invalid save! Exiting...")
        exit