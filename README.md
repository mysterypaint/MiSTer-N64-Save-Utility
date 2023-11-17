# MiSTer N64 Save Utility
 A Python-based utility to inject and dump N64 ControllerPak/TransferPak saves for the MiSTer FPGA.

## Casual Usage (Windows Users only)
1) Ensure that [Python](https://www.python.org/downloads/) is installed.
2) Download the most recent version of [N64-Database.txt](https://raw.githubusercontent.com/MiSTer-devel/N64_ROM_Database/main/N64-database.txt) and place it in the same folder as ``convert_tpak_data.py``.
3) Create a copy of ``Input_EXAMPLE.ini`` and then rename the copy to ``Input.ini``.
4) Edit ``Input.ini`` in your favorite text editor. Please read all of the comments carefully as you fill it out!
5) Double-click on ``launch.bat``. If you filled out the form correctly, your new save file should be at the path you specified for ``OutputN64SavePath``.

## Usage via Terminal/CLI
```usage: convert_tpak_data.py [-h] [-n64 [N64]] [-o [O]] [-cid [CID]] [-mpk [MPK]] [-gb [GB]] [-d] [-gi]```

### options:<br>
    -h, --help  show this help message and exit
    -n64 [N64]  Input N64 Save Path  |  (Default: "N64_In.sav")
    -o [O]      Output Save Path  |  (Default: "Output.sav")
    -cid [CID]  N64 Cart ID  |  (Default: "")
    -mpk [MPK]  Input CPak Save Path (Comma-separated; Max: 4)  |  (Default: "MPK_in.sav")
    -gb [GB]    Input GB Save Path  |  (Default: "GB_in.sav")
    -d          Flag: The GB save should be dumped from the N64 save  |  (Default: False)
    -gi         Flag: The GB save should be injected into the N64 save  |  (Default: False)
    -ini        Flag: Override all other arguments with data from Input.ini  |  (Default: False)

### Example Terminal/CLI Usage
``python convert_n64_savedata.py -i -n64 -cid "NP3___" "N64.sav" -gb "GB_in.sav"``<br>
^^^The above example will inject ``GB_in.sav`` into ``N64.sav`` as ``Pokemon Stadium 2 (NP3___)`` and output it as ``Output.sav``.

``python convert_n64_savedata.py -d -n64 -cid "NP3___" "N64.sav" -o "GB_out.sav"``<br>
^^^The above example will dump the Gameboy Save from ``N64.sav`` as ``Pokemon Stadium 2 (NP3___)`` and output it as ``GB_out.sav``.

``python convert_n64_savedata.py -n64 "MK64_In.sav" -cid "NKT___" -mpk "moomoofarm_wariostadium.mpk,*cpakTestBak1_LuigiRaceway.mpk"``
^^^The above example will inject ``moomoofarm_wariostadium.mpk`` and ``cpakTestBak1_LuigiRaceway.mpk`` into ``N64.sav`` as ``Mario Kart 64 (NKT___)`` and output it as ``Output.sav``. ``cpakTestBak1_LuigiRaceway.mpk`` will be injected with flipped endian bytes because it has a ``*`` at the start of its path.

## License
[MIT](https://choosealicense.com/licenses/mit/)