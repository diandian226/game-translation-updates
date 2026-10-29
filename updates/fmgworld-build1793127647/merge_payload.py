"""Combine known ZIP entries without recompressing; identical bytes on Windows and CI."""
import hashlib, io, struct, sys, zipfile
from pathlib import Path

BASE_SHA = "c98796e12ee793c34b7d83807379798c53e39ea2c2d19be90cbb28c97c285989"

def entries(blob):
    result = {}
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        if z.testzip() is not None:
            raise ValueError("ZIP CRC check failed")
        info = z.infolist()
        assert len({i.filename for i in info}) == len(info)
        position = z.start_dir
        blocks = sorted(info, key=lambda i: i.header_offset)
        ends = {i.filename: blocks[n+1].header_offset if n+1 < len(blocks) else z.start_dir for n,i in enumerate(blocks)}
        for item in info:
            name = item.filename
            assert name.startswith("assets/x-game/") and ".." not in name and "\\" not in name
            assert blob[position:position+4] == b"PK\x01\x02"
            lengths = struct.unpack_from("<HHH", blob, position+28)
            end = position+46+sum(lengths)
            result[name] = (blob[item.header_offset:ends[name]], blob[position:end])
            position = end
    return result

def merge(base, delta, output):
    raw = Path(base).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == BASE_SHA
    table = entries(raw)
    table.update(entries(Path(delta).read_bytes()))
    central = []
    with Path(output).open("wb") as out:
        for name in sorted(table):
            local, header = table[name]
            header = bytearray(header)
            struct.pack_into("<I", header, 42, out.tell())
            central.append(header)
            out.write(local)
        start = out.tell()
        for header in central:
            out.write(header)
        out.write(struct.pack("<4s4H2IH", b"PK\x05\x06", 0, 0, len(table), len(table), out.tell()-start, start, 0))
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
    print("payload SHA256:", hashlib.sha256(Path(output).read_bytes()).hexdigest())

if __name__ == "__main__":
    merge(*sys.argv[1:4])
