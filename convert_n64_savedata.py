import os, sys, argparse, configparser, shutil
from enum import Enum
from pathlib import Path

SaveState = Enum('SaveState', ['NO_INJECTION', 'HAS_INJECTION', 'INVALID'])
FlashSaves = Enum('FlashSaves', ['EEPROM_512', 'EEPROM_2K', 'SRAM_32K', 'SRAM_96K', 'FLASH_128K', 'NOTHING'])

def cleanIniData(strIn):
    return strIn.split(";")[0].strip()

def checkIfCanInject(tPak, cPak):
    if (not tPak and not cPak):
        raise Exception("This game does not support tPaks nor cPaks: Cannot inject anything!")

def populateN64Database():
    if not os.path.isfile("N64-database.txt"):
        raise Exception("N64-database.txt is not found! Please place it in the same folder as this Python script. You can download it at:\nhttps://raw.githubusercontent.com/MiSTer-devel/N64_ROM_Database/main/N64-database.txt")
    else:
        N64Database = []
        # TODO: Determine the flash type based on the filename (should be Cart ID)
        with open("N64-database.txt") as file:
            for line in file:
                if line.startswith("ID:"):
                    romData = line.rstrip().split(":")[1].split(" ")
                    cartID = romData[0]
                    saveTypes = romData[1].split("|")
                    try:
                        romName = line.split('#')[1].strip()
                    except IndexError:
                        romName = "Unknown Homebrew"
                    N64Database.append([cartID, saveTypes, romName])
                elif len(line) > 0:
                    if not line.startswith("#") and not line.isspace() and "#" in line:
                        romData = line.rstrip().split(" ")
                        md5Hash = romData[0]
                        saveTypes = romData[1].split("|")
                        romName = line.split('#')[1].strip()
                        N64Database.append(["md5", md5Hash, saveTypes, romName])
        return N64Database

def determineN64Flashsave(N64Database, inCartID):
        isMD5 = False
        romName = "Unknown"

        for romData in N64Database:
            if (romData[0] == "md5"):
                if (romData[1] == inCartID):
                    saveTypes = romData[2]
                    romName = romData[3]
                    isMD5 = True
                    print("Using save structure for:", romName, "(" + inCartID + ")")
                    break
            elif (romData[0] == inCartID):
                saveTypes = romData[1]
                romName = romData[2]
                print("Using save structure for:", romName, "(" + inCartID + ")")
                break
        
        if (romName == "Unknown"):
            raise Exception("\n\nCould not identify the Cart ID: " + inCartID + "\nPlease either ensure you entered it correctly in Input.ini, or manually add it to N64-Database.txt")

        # Could get region/security chip data here, if ever relevant (would use "isMD5")

        flashType = FlashSaves.NOTHING
        cPak = False
        tPak = False
        rPak = False
        rtc = False

        for saveType in saveTypes:
            match(saveType):
                case "eeprom512":
                    flashType = FlashSaves.EEPROM_512
                case "eeprom2k":
                    flashType = FlashSaves.EEPROM_2K
                case "sram32k":
                    flashType = FlashSaves.SRAM_32K
                case "sram96k":
                    flashType = FlashSaves.SRAM_96K
                case "flash128k":
                    flashType = FlashSaves.FLASH_128K
                case "cpak":
                    cPak = True
                case "tpak":
                    tPak = True
                case "rtc":
                    rtc = True
        return [flashType, cPak, tPak, rPak, rtc]

def padN64Save(savePathN64, flashSave):
    fileSize = os.path.getsize(savePathN64)
    flashSize = 0x0
    match(flashSave):
        case FlashSaves.NOTHING:
            exit
        case FlashSaves.EEPROM_512:
            flashSize = 0x200
        case FlashSaves.EEPROM_2K:
            flashSize = 0x800
        case FlashSaves.SRAM_32K:
            flashSize = 0x8000
        case FlashSaves.SRAM_96K:
            flashSize = 0x18000
        case FlashSaves.FLASH_128K:
            flashSize = 0x20000
    
    expansionSize = 0x20000

    if ((flashSize + expansionSize) > fileSize):
        with open(savePathN64, 'a+') as f:
            f.write('\0' * ((flashSize - fileSize) + expansionSize))
            f.close()
            print("Output save padded to", hex(flashSize  + expansionSize), "bytes! (", flashSize  + expansionSize, "bytes )")
    elif ((flashSize + expansionSize) <= fileSize):
        print("[Warning] Injection detected! Any existing [C/T]Pak saves will be overwritten...")
    return flashSize

def dumpPakSaves(savePathN64, savePathOut, N64FlashSave):
    try:
        # Write the contents of the N64 Save into the GB Save and format it accordingly
        fileSize = os.path.getsize(savePathN64)
        flashSize = 0x0
        match(N64FlashSave):
            case FlashSaves.NOTHING:
                exit
            case FlashSaves.EEPROM_512:
                flashSize = 0x200
            case FlashSaves.EEPROM_2K:
                flashSize = 0x800
            case FlashSaves.SRAM_32K:
                flashSize = 0x8000
            case FlashSaves.SRAM_96K:
                flashSize = 0x18000
            case FlashSaves.FLASH_128K:
                flashSize = 0x20000
        
        expansionSize = 0x20000

        if (fileSize > flashSize + expansionSize):
            print("[Warning] Save file is larger than expected! Dumping save might not work reliably...")

        dirPath, fName = os.path.split(savePathOut)
        rawName = str(Path(fName).stem)
        outFNames = [
            fName,
            rawName + " (Port 2).sav",
            rawName + " (Port 3).sav",
            rawName + " (Port 4).sav"
        ]
        printedNames = ""
        i = 0
        for outFName in outFNames:
            saveFileGB = open(Path(dirPath, outFName), "wb")
            with open(savePathN64, 'br') as f:
                f.seek(0x00020000)
                data = f.read(4)
                for offset in range(0x00020000, 0x00027FFF, 0x4):
                    saveFileGB.write(data[::-1])
                    data = f.read(4)
            saveFileGB.close()
            i += 1
            printedNames += str(Path(dirPath, outFName))
            if i < 4:
                printedNames += "\n"
        print("\nSuccess! Dumped all [C/T]Pak saves to:\n" + printedNames)
    except FileNotFoundError:
        print("File not found.")
    except OSError:
        print("OS error occurred.")

def injectMPKSaves(savePathN64, savePathOut, mpkFiles, N64FlashSave):
    if (len(mpkFiles) > 4):
        raise Exception("Trying to inject too many [C/T]Paks! Max: 4")

    # Back up the N64 save before we inject anything
    shutil.copyfile(savePathN64, savePathOut)

    # Pad the end of the file with zeros if we never injected a GB Save into this N64 Save
    flashSize = padN64Save(savePathOut, N64FlashSave)

    # Open the N64 In/Out saves, for Reading+Writing
    saveFileN64Orig = open(savePathN64, "rb")
    saveFileN64Out = open(savePathOut, "wb")
    
    # Clone the original save data to the new save
    data = saveFileN64Orig.read(flashSize)
    saveFileN64Out.write(data)
    
    # Write the injection data immediately after the flash save data
    mpksToWrite = []
    mpksToWriteString = ""
    numMpks = 0
    for mpkFile in mpkFiles:
        flipMe = True
        if (len(mpkFile) > 0):
            if (mpkFile[0] == "*"):
                flipMe = False
                mpkFile = mpkFile[1:len(mpkFile)]
            mpksToWrite.append([mpkFile, flipMe])
            mpksToWriteString += " " + str(numMpks) + ": " + mpkFile.lstrip() + "  |  Flip bytes: " + str(flipMe) + "\n "
            numMpks += 1
        else:
            mpksToWrite.append(["blank.cpak", False])
            mpksToWriteString += " " + str(numMpks) + ": blank.cpak  |  Flip bytes: False\n "
            numMpks += 1

    
    # If we have any unassigned TPaks/CPaks, inject a pre-formatted empty Pak in its place
    while(numMpks < 4):
        mpksToWrite.append(["blank.cpak", False])
        mpksToWriteString += " " + str(numMpks) + ": blank.cpak  |  Flip bytes: False\n "
        numMpks += 1

    # Let the user know what we're doing
    print("\nInjecting [C/T]Paks:\n", mpksToWriteString)
    print("Flash Size:", flashSize, "bytes")

    # Inject the data we've calculated/prepared, starting at the end of the Flash Save file. Each Pak save file is 0x8000 bytes long.
    injectRangeBegin = flashSize
    injectRangeEnd = injectRangeBegin + 0x7FFF

    for cPakInjection in mpksToWrite:
        cPakPath = cPakInjection[0]
        flipEndianness = cPakInjection[1]
        
        gbChunkSize = 0
        
        if (cPakPath[0] == "*"):
            cPakPath = cPakPath[1:len(cPakPath)]
        with open(cPakPath, 'br') as f:
            gbChunkSize = os.stat(cPakPath).st_size
            blockSize = 0x4
            data = f.read(blockSize)
            for offset in range(injectRangeBegin, injectRangeEnd, blockSize):
                if flipEndianness:
                    saveFileN64Out.write(data[::-1])
                else:
                    saveFileN64Out.write(data)
                data = f.read(4)
            f.close()
            injectRangeBegin += 0x8000
            injectRangeEnd += 0x8000

    saveFileN64Out.close()
    print("Done! Written to: " + savePathOut)

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle

savePathN64In = ''
savePathMPK = ''
savePathOut = ''
inCartID = ''
dumpMPKEnabled = False
injectMPKEnabled = False

parser = argparse.ArgumentParser("convert_tpak_data.py")
parser.add_argument("-n64", help="Input N64 Save Path", nargs='?', default="N64_In.sav")
parser.add_argument("-o", help="Output Save Path", nargs='?', default="Output.sav")
parser.add_argument("-cid", help="N64 Cart ID", nargs='?', default='')
parser.add_argument("-mpk", help="Input [C/T]Pak Save Path (Comma-separated; Max: 4)", nargs='?', default="")
parser.add_argument('-d', help="Flag: The MPK (and TPak Gameboy) saves should be dumped from the N64 save", action='store_true', default=False)
parser.add_argument('-ini', help="Flag: Override all other arguments with data from Input.ini", action='store_true', default=False)

if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    exit

args = parser.parse_args()

if (args.ini):
    if not os.path.exists('Input.ini'):
        raise Exception("Input.ini was not found! Aborting...")
    config = configparser.ConfigParser()
    config.read('Input.ini')
    savePathN64In = cleanIniData(config['PATHS']['InputN64SavePath'])
    savePathOut = cleanIniData(config['PATHS']['OutputSavePath'])
    inCartID = cleanIniData(config['CART_ID']['CartID'])
    
    dumpMPKEnabled = cleanIniData(config['OPTIONS']['DumpSaves'])
    if (dumpMPKEnabled == "T"):
        dumpMPKEnabled = True
    else:
        dumpMPKEnabled = False
    
    tP1 = cleanIniData(config['TPAKS']['TPak1'])
    tP2 = cleanIniData(config['TPAKS']['TPak2'])
    tP3 = cleanIniData(config['TPAKS']['TPak3'])
    tP4 = cleanIniData(config['TPAKS']['TPak4'])
    TPaks = [tP1, tP2, tP3, tP4]

    cP1 = cleanIniData(config['CPAKS']['CPak1'])
    cP2 = cleanIniData(config['CPAKS']['CPak2'])
    cP3 = cleanIniData(config['CPAKS']['CPak3'])
    cP4 = cleanIniData(config['CPAKS']['CPak4'])
    CPaks = [cP1, cP2, cP3, cP4]

    mpkFiles = TPaks
    injectMPKEnabled = True
    blankPaks = 0
    for tpak in mpkFiles:
        if tpak == "":
            blankPaks +=1
    if blankPaks >= 4:
        mpkFiles = CPaks
        blankPaks = 0
        for cpak in mpkFiles:
            if cpak == "":
                blankPaks +=1
        if blankPaks >= 4:
            mpkFiles = []
            injectMPKEnabled = False
else:
    if (args.n64 == "N64_In.sav" or args.n64 == None or args.n64 == ""):
        savePathN64In = "N64_In.sav"
    else:
        savePathN64In = args.n64
    if (args.o == "Output.sav" or args.o == None or args.o == ""):
        savePathOut = "Output.sav"
    else:
        savePathOut = args.o
    if (args.mpk == "MPK_in.sav" or args.mpk == None or args.mpk == ""):
        savePathMPK = "MPK_in.sav"
    else:
        savePathMPK = args.mpk

    inCartID = args.cid
    dumpMPKEnabled = args.d

    mpkFiles = []
    if (args.mpk != ""):
        injectMPKEnabled = True
        mpkFiles = args.mpk.split(",")


N64FlashSave = FlashSaves.NOTHING
if os.path.isfile(savePathN64In):
    if (inCartID == ''):
        raise Exception("Aborting: Please provide a Cart ID.")
    N64Database = populateN64Database()
    
    # Returns array: [flashType, cPak, tPak, rPak, rtc]
    N64CartSaveParams = determineN64Flashsave(N64Database, inCartID)
    
    N64FlashSave = N64CartSaveParams[0]
    cPak = N64CartSaveParams[1]
    tPak = N64CartSaveParams[2]
    rPak = N64CartSaveParams[3]
    rtc = N64CartSaveParams[4]
    
    match(N64FlashSave):
        case FlashSaves.NOTHING:
            if (dumpMPKEnabled):
                print("There is no Injected Save to dump! Aborting...")
                exit
            if (injectMPKEnabled):
                checkIfCanInject(cPak, tPak)
                print("Injecting MPK Save(s) into: " + savePathOut)
                injectMPKSaves(savePathN64In, savePathOut, mpkFiles, FlashSaves.NOTHING)
            exit
        case FlashSaves.EEPROM_512 | FlashSaves.EEPROM_2K | FlashSaves.SRAM_32K | FlashSaves.SRAM_96K | FlashSaves.FLASH_128K:
            if (dumpMPKEnabled):
                print("Dumping Pak Saves from: " + savePathN64In)
                dumpPakSaves(savePathN64In, savePathOut, N64FlashSave)
            elif (injectMPKEnabled):
                checkIfCanInject(cPak, tPak)
                print("Injecting MPK Save(s) into: " + savePathN64In)
                injectMPKSaves(savePathN64In, savePathOut, mpkFiles, N64FlashSave)
            exit
else:
    print("Input N64 Save was not found: " + savePathN64In + "\nAborting...")