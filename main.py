
import math
import os
import struct
import zlib


WIDTH = 768
HEIGHT = 768


def make_chunk(chunk_type, data):
    chunk = chunk_type + data
    crc = zlib.crc32(chunk) & 0xffffffff
    return (
        struct.pack(">I", len(data))
        + chunk
        + struct.pack(">I", crc)
    )


def create_image():
    rows = []

    for y in range(HEIGHT):
        row = bytearray([0])

        for x in range(WIDTH):
            nx = (x - WIDTH / 2) / (WIDTH / 2)
            ny = (y - HEIGHT / 2) / (HEIGHT / 2)

            radius = math.sqrt(nx * nx + ny * ny)
            wave = math.sin(radius * 18 - math.atan2(ny, nx) * 5)

            glow = max(0, 1 - radius)
            r = int(15 + 35 * glow + 15 * wave)
            g = int(20 + 100 * glow + 20 * wave)
            b = int(45 + 180 * glow + 25 * wave)

            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))

            row.extend((r, g, b))

        rows.append(bytes(row))

    raw_data = b"".join(rows)

    png = (
        b"\x89PNG\r\n\x1a\n"
        + make_chunk(
            b"IHDR",
            struct.pack(
                ">2I5B",
                WIDTH,
                HEIGHT,
                8,
                2,
                0,
                0,
                0
            )
        )
        + make_chunk(b"IDAT", zlib.compress(raw_data, 9))
        + make_chunk(b"IEND", b"")
    )

    return png


def main():
    output_dir = os.environ.get(
        "MAKEFUN_OUTPUT_DIR",
        "/output" if os.path.isdir("/output") else "output"
    )

    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(
        output_dir,
        "entry.png"
    )

    image = create_image()

    with open(output_file, "wb") as file:
        file.write(image)

    print("Image generated:", output_file)
    print("Dimensions:", WIDTH, "x", HEIGHT)
    print("File size:", len(image), "bytes")

    if len(image) > 1024 * 1024:
        raise ValueError("Image exceeds 1 MiB limit")


if __name__ == "__main__":
    main()
