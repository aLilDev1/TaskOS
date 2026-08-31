from pathlib import Path
import re

"""
Directory must have this exact layout:

directory/
  XXXX-ID/
    XXXX-ID.ext
    
XXXX is just a 4 letter name, can include numbers
ID is a index identifier, done as hexadecimal
.ext is just the extension for the file, ignored, doesn't care what this is

Resulting file should be used with the ".lib" extension, or the ".xlib" extension, the ".xlib" extension is for future improvments of this format.... or this compiler

"""

DirectoryPath = r""
OutputPath = r""

def load_directory(root_path):
    root = Path(root_path)
    result = {}
    directory_pattern = re.compile(
        r"^([A-Za-z0-9]{4})-([0-9A-Fa-f]{2})$"
    )
    file_pattern = re.compile(
        r"^([A-Za-z0-9]{4})-([0-9A-Fa-f]{2})\.[^.]+$"
    )
    for directory in root.iterdir():
        if not directory.is_dir():
            continue
        directory_match = directory_pattern.fullmatch(directory.name)
        if not directory_match:
            continue
        region_name = directory_match.group(1)
        region_index = int(directory_match.group(2), 16)
        files = [f for f in directory.iterdir() if f.is_file()]
        if not files:
            continue
        file = files[0]
        file_match = file_pattern.fullmatch(file.name)
        if not file_match:
            continue
        sub_name = file_match.group(1)
        sub_index = int(file_match.group(2), 16)
        file_data = file.read_bytes()
        result[region_index] = (
            region_name,
            {
                sub_index: (
                    sub_name,
                    file_data,
                ),
            },
        )
    return result



data = load_directory(DirectoryPath)
dataregion = bytearray()
structureregion = bytearray()
structure = {
}

for key, (name, sub_data) in data.items():
    for sub_key, (sub_name, data) in sub_data.items():
        offset = len(dataregion)
        dataregion.append(0x03)
        dataregion.extend(len(data).to_bytes(8, byteorder="big"))
        dataregion.extend(data)
        dataregion.append(0x04)
        structureadd = {
            key: (name, {
                sub_key: (sub_name, offset,),
            },),
        }
        structure.update(structureadd)

for key, (name, sub_data) in structure.items():
    tempsubregion = bytearray()
    for sub_key, (sub_name, offset) in sub_data.items():
        tempsubregion.extend(sub_key.to_bytes(4, byteorder="big"))
        tempsubregion.extend(sub_name.encode("ascii"))
        tempsubregion.extend(offset.to_bytes(8, byteorder="big"))
    structureregion.append(0x01)
    structureregion.extend(key.to_bytes(2, byteorder="big"))
    structureregion.extend(name.encode("ascii"))
    structureregion.extend(len(tempsubregion).to_bytes(8, byteorder="big"))
    structureregion.extend(tempsubregion)
    structureregion.append(0x02)
    

with open(OutputPath, "wb") as f:
    x = len(dataregion) + 0x20
    f.write(x.to_bytes(8, byteorder="big"))
    x = len(structureregion)
    f.write(x.to_bytes(8, byteorder="big"))
    f.write(0x20.to_bytes(8, byteorder="big"))
    x = len(dataregion)
    f.write(x.to_bytes(8, byteorder="big"))
    f.write(dataregion)
    f.write(structureregion)