# MiSTer N64 TransferPak Utility
 A Python-based utility to convert N64 TransferPak saves for the MiSTer FPGA

## Casual Usage (Windows Users only)
### To Inject a Save
For friendly usage, I have provided two, Windows-based .bat scripts:
1) Ensure that [Python](https://www.python.org/downloads/) is installed.
2) Place your N64 Save File (e.g. Pokemon Stadium) in the same folder as ``convert_tpak_data.py`` and rename it to ``N64_TPak.sav``
3) Place your GB Save File (e.g. Pokemon Yellow) in the same folder as ``convert_tpak_data.py`` and rename it to ``GB_in.sav``
4) Double-click on ``gb_save_inject.bat`` and wait.
5) Your injected save will be in the same folder as the Python script as ``N64_TPak.sav``. A backup of the save, prior to injection, will also be in the same folder, as ``N64_TPak_pre-injection.sav``


### To Dump a Save
1) Ensure that [Python](https://www.python.org/downloads/) is installed.
2) Place your N64 Save File (e.g. Pokemon Stadium) in the same folder as ``convert_tpak_data.py`` and rename it to ``N64_TPak.sav``
3) Double-click on ``gb_save_dump.bat`` and wait.
4) Your dumped save will be in the same folder as the Python script as ``GB_out.sav``

## Usage via Terminal/CLI
```convert_tpak_data.py [-h] [-n64 [N64]] [-gb [GB]] [-d] [-i] [-exp [EXP]]```

### options:<br>
    -h, --help  show this help message and exit
    -n64 [N64]  Input & Output N64 Save Path  |  (Default: "N64_TPak.sav")
    -gb [GB]    Input GB Save Path  |  (Default: "GB_in.sav")
    -d          Flag: The GB save should be dumped from the N64 save  |  (Default: False)
    -i          Flag: The GB save should be injected into the N64 save  |  (Default: False)
    -exp [EXP]  Path to export GB Save Dump from N64 Save  |  (Default: "GB_out.sav")

### Example
``python convert_tpak_data.py -i -n64 "N64_TPak.sav" -gb "GB_in.sav"``<br>
^^^The above example will inject ``GB_in.sav`` into ``N64_TPak.sav``

## License
[MIT](https://choosealicense.com/licenses/mit/)