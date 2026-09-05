from pathlib import Path
import re

"""
Directory must have this exact layout:

directory/
  XXXX...-IDIDIDID
    XXXX...-IDIDIDID.ext
    
XXXX is just a name, cannot include "-", must be A-Z, a-z, 0-9, and _.
ID is a index identifier, done as hexadecimal, 32 bit.
.ext is just the extension for the file, ignored, doesn't care what this is

Resulting file should be used with the ".lib" extension, or the ".xlib" extension, the ".xlib" extension is for future improvments of this format.... or this compiler

"""

DirectoryPath = r""
OutputPath = r""

def parse_directory(directory):
    region_pattern = re.compile(r"^([A-Za-z0-9_]+)-([0-9A-Fa-f]+)$")
    file_pattern = re.compile(r"^([A-Za-z0-9_]+)-([0-9A-Fa-f]+)(?:\.[^.]+)?$")
    result = {}
    for region_dir in Path(directory).iterdir():
        if not region_dir.is_dir():
            continue
        match = region_pattern.fullmatch(region_dir.name)
        if not match:
            raise ValueError(
                f"Invalid region directory: {region_dir.name!r}"
            )
        region_name, region_index_hex = match.groups()
        region_index = int(region_index_hex, 16)
        files = {}
        for file in region_dir.iterdir():
            if not file.is_file():
                continue
            match = file_pattern.fullmatch(file.name)
            if not match:
                raise ValueError(
                    f"Invalid file name: {file.name!r}"
                )
            file_name, file_index_hex = match.groups()
            file_index = int(file_index_hex, 16)
            file_data = file.read_bytes()
            files[file_index] = (file_name, file_data)
        result[region_index] = (region_name, files)
    return result

data = parse_directory(DirectoryPath)
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
        if key not in structure:
            structure[key] = (name, {})

        structure[key][1].update({
            sub_key: (sub_name, offset)
        })

for key, (name, sub_data) in structure.items():
    tempsubregion = bytearray()
    for sub_key, (sub_name, offset) in sub_data.items():
        tempsubregion.extend(sub_key.to_bytes(4, byteorder="big"))
        tempsubregion.extend(len(sub_name).to_bytes(1, byteorder="big"))
        tempsubregion.extend(sub_name.encode("ascii"))
        tempsubregion.extend(offset.to_bytes(8, byteorder="big"))
    structureregion.append(0x01)
    structureregion.extend(key.to_bytes(4, byteorder="big"))
    structureregion.extend(len(name).to_bytes(1, byteorder="big"))
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