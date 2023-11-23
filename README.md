# MiSTer N64 Save Utility
 A Python-based utility to inject and dump N64 ControllerPak/TransferPak saves for the MiSTer FPGA.

## Casual Usage
1) [Download this repo](https://github.com/mysterypaint/MiSTer-N64-Save-Utility/archive/refs/heads/main.zip) and extract its ``.zip`` archive contents anywhere on your PC.
2) Ensure that [Python](https://www.python.org/downloads/) is installed.
3) Download the most recent version of [N64-Database.txt](https://raw.githubusercontent.com/MiSTer-devel/N64_ROM_Database/main/N64-database.txt) and place it in the same folder as ``convert_tpak_data.py``.
4) Create a copy of ``Input_EXAMPLE.ini`` and then rename the copy to ``Input.ini``.
5) Edit ``Input.ini`` in your favorite text editor. Please read all of the comments carefully as you fill it out!
6) (Windows Users only) Double-click on ``launch.bat``.
    - For Linux/Mac/Other: ``convert_tpak_data.py -ini``

If you filled out the form correctly, your new save file(s) should be at the path you specified for ``OutputSavePath``.

## Expert Usage via Terminal/CLI
```convert_tpak_data.py [-h] [-n64 [N64]] [-o [O]] [-cid [CID]] [-mpk [MPK]] [-d] [-ini]```

### options:<br>
    -h, --help  show this help message and exit
    -n64 [N64]  Input N64 Save Path  |  (Default: "N64_In.sav")
    -o [O]      Output Save Path  |  (Default: "Output.sav")
    -cid [CID]  N64 Cart ID  |  (Default: "")
    -mpk [MPK]  Input [C/T]Pak Save Path (Comma-separated; Max: 4)  |  (Default: "MPK_in.sav")
    -d          Flag: The MPK (and TPak Gameboy) saves should be dumped from the N64 save  |  (Default: False)
    -ini        Flag: Override all other arguments with data from Input.ini  |  (Default: False)

### Example Terminal/CLI Usage
``python convert_n64_savedata.py -n64 "N64.sav" -cid "NP3___" -mpk "GB_in.sav"``<br><br>
The above example will inject ``GB_in.sav`` into ``N64.sav`` as ``Pokemon Stadium 2 (NP3___)`` and output it as ``Output.sav``.

``python convert_n64_savedata.py -d -n64 "N64.sav" -cid "NP3___" -o "GB_out.sav"``<br><br>
The above example will dump the Gameboy Save from ``N64.sav`` as ``Pokemon Stadium 2 (NP3___)`` and output it as ``GB_out.sav``. The remaining 3 controller ports' saves will also be output under this name, but slightly renamed to differentiate them.

``python convert_n64_savedata.py -n64 "MK64_In.sav" -cid "NKT___" -mpk "moomoofarm_wariostadium.mpk,*cpakTestBak1_LuigiRaceway.mpk"``<br><br>
The above example will inject ``moomoofarm_wariostadium.mpk`` and ``cpakTestBak1_LuigiRaceway.mpk`` into ``N64.sav`` as ``Mario Kart 64 (NKT___)`` and output it as ``Output.sav``.<br>Additionally, ``cpakTestBak1_LuigiRaceway.mpk`` will be injected with flipped endian bytes, because it has a ``*`` at the start of its path.

## License
[MIT](https://choosealicense.com/licenses/mit/)