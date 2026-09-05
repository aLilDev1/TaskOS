from pathlib import Path

"""
Resulting directory should have this layout:

directory/
  XXXX...-IDIDIDID
    XXXX...-IDIDIDID
    
Read LibCompile.py for more info...


Im sorry to say this but this was AI, based off the LibCompile, I just needed a quick decompiler to make sure nothing got corrupted on the other end.
At least I was honest?
"""

InputPath = r"C:\Users\Silas\Documents\Projects\AmberWood\TaskOS\Drive\TaskOS\Boot\BootGraphics.Lib"
OutputPath = r"C:\Users\Silas\Desktop\BootGraphics"


with open(InputPath, "rb") as f:
    raw = f.read()

structure_offset = int.from_bytes(raw[0x00:0x08], byteorder="big")
structure_size = int.from_bytes(raw[0x08:0x10], byteorder="big")
data_offset = int.from_bytes(raw[0x10:0x18], byteorder="big")
data_size = int.from_bytes(raw[0x18:0x20], byteorder="big")

dataregion = raw[data_offset:data_offset + data_size]
structureregion = raw[
    structure_offset:structure_offset + structure_size
]

structure = {}

pos = 0

while pos < len(structureregion):
    if structureregion[pos] != 0x01:
        raise ValueError("Invalid region start marker")
    pos += 1

    key = int.from_bytes(
        structureregion[pos:pos + 4],
        byteorder="big"
    )
    pos += 4

    name_length = structureregion[pos]
    pos += 1

    name = structureregion[
        pos:pos + name_length
    ].decode("ascii")
    pos += name_length

    subregion_size = int.from_bytes(
        structureregion[pos:pos + 8],
        byteorder="big"
    )
    pos += 8

    subregion_end = pos + subregion_size

    files = {}

    while pos < subregion_end:
        sub_key = int.from_bytes(
            structureregion[pos:pos + 4],
            byteorder="big"
        )
        pos += 4

        sub_name_length = structureregion[pos]
        pos += 1

        sub_name = structureregion[
            pos:pos + sub_name_length
        ].decode("ascii")
        pos += sub_name_length

        offset = int.from_bytes(
            structureregion[pos:pos + 8],
            byteorder="big"
        )
        pos += 8

        files[sub_key] = (sub_name, offset)

    if structureregion[pos] != 0x02:
        raise ValueError("Invalid region end marker")
    pos += 1

    structure[key] = (name, files)

for key, (name, files) in structure.items():

    region_directory = (
        Path(OutputPath) /
        f"{name}-{key:08X}"
    )

    region_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    sorted_files = sorted(
        files.items(),
        key=lambda x: x[1][1]
    )

    for i, (sub_key, (sub_name, offset)) in enumerate(sorted_files):

        if dataregion[offset] != 0x03:
            raise ValueError(
                f"Invalid data marker at offset {offset}"
            )

        size = int.from_bytes(
            dataregion[offset + 1:offset + 9],
            byteorder="big"
        )

        data_start = offset + 9
        data_end = data_start + size

        if dataregion[data_end] != 0x04:
            raise ValueError(
                f"Invalid data end marker at offset {data_end}"
            )

        file_data = dataregion[data_start:data_end]

        output_file = (
            region_directory /
            f"{sub_name}-{sub_key:08X}"
        )

        output_file.write_bytes(file_data)