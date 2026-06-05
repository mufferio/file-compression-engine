# File Compression Engine

A Python quadtree-based image compression project that converts BMP images to grayscale, compresses them into a custom `.qdt` format, and reconstructs BMP images from the compressed representation.

## Overview

This repository implements a small image-compression pipeline centered on a quadtree data structure:

1. A BMP image is loaded from disk.
2. Each RGB pixel is converted to a single grayscale intensity.
3. The grayscale matrix is recursively compressed into a quadtree.
4. The tree is serialized into a custom `.qdt` file that preserves the original BMP header.
5. The `.qdt` file can be decompressed back into a grayscale BMP image.

The current implementation also enables image mirroring during compression (`MIRROR_IMG = True`), so the reconstructed image mirrors the bottom half into the top half.

## Key Capabilities

- **BMP ingestion** through a lightweight binary parser
- **Lossy grayscale compression** driven by a configurable `loss_level`
- **Quadtree serialization** into a custom file format
- **BMP reconstruction** from compressed quadtree data
- **Built-in mirroring support** enabled in the current compression flow
- **Sample assets** included for experimentation

## Repository Contents

| Path | Purpose |
| --- | --- |
| `/tmp/workspace/mufferio/file-compression-engine/a2main.py` | CLI entry point plus `Compressor` and `Decompressor` orchestration logic |
| `/tmp/workspace/mufferio/file-compression-engine/a2tree.py` | Core quadtree implementation, compression logic, traversal, restore, and loss analysis |
| `/tmp/workspace/mufferio/file-compression-engine/a2files.py` | BMP/QDT file parsing, metadata extraction, serialization, and persistence |
| `/tmp/workspace/mufferio/file-compression-engine/test.py` | Small local script for manually inspecting quadtree structure |
| `/tmp/workspace/mufferio/file-compression-engine/dog.bmp` | Sample bitmap image |
| `/tmp/workspace/mufferio/file-compression-engine/toronto.bmp` | Sample bitmap image |
| `/tmp/workspace/mufferio/file-compression-engine/uoft.bmp` | Sample bitmap image |
| `/tmp/workspace/mufferio/file-compression-engine/toronto-children.png` | Additional image asset |

## How the Compression Works

### 1. BMP loading

`BMPFile` reads:

- the pixel data offset from bytes `10-13`
- image width from bytes `18-21`
- image height from bytes `22-25`
- the header bytes that will later be reused when saving output

The bitmap body is converted into a 2D matrix of RGB tuples.

### 2. Grayscale conversion

`Compressor.convert_grayscale_single` transforms each pixel from `(r, g, b)` to one grayscale value using:

`0.2126 * red + 0.7152 * green + 0.0722 * blue`

That value is rounded and then reused as all three channels during decompression.

### 3. Quadtree construction

`QuadTree.build_quad_tree` recursively subdivides the grayscale matrix into:

- bottom-left
- bottom-right
- top-left
- top-right

Each region is compressed into a `QuadTreeNodeLeaf` when its **standard deviation is less than or equal to** `loss_level`. Otherwise it becomes a `QuadTreeNodeInternal` and is subdivided further.

If a region is empty, it becomes `QuadTreeNodeEmpty`.

### 4. Mirroring

After the tree is built, the current code mirrors the image by copying the bottom half into the top half. This behavior is controlled by `MIRROR_IMG` in `/tmp/workspace/mufferio/file-compression-engine/a2main.py` and is currently set to `True`.

### 5. Serialization

`QuadTreeFile` stores:

- the original BMP header
- the quadtree serialized as a preorder string

Preorder tokens are encoded as:

- `""` for an internal node
- `"E"` for an empty node
- `"number"` for a leaf node intensity

Example preorder:

`,E,5,8,E`

## Compression Model

The project is **lossy** for two reasons:

1. It converts the source image to grayscale.
2. It merges image regions when their pixel variance is within the configured `loss_level`.

### `loss_level` behavior

- `0` preserves much more detail and produces larger trees/files.
- Larger values allow more aggressive merging and smaller output files.
- Accepted range: `0` to `255`.

## Input and Output Formats

### Supported input

- `.bmp` files for compression
- `.qdt` files for decompression

### Produced output

- Compression writes: `<input>.bmp.qdt`
- Decompression writes: `<input>.qdt.bmp`

## Running the Project

### Requirements

- Python 3
- No required third-party runtime dependency for compression/decompression

### CLI usage

Run:

```bash
python /tmp/workspace/mufferio/file-compression-engine/a2main.py
```

You will be prompted to:

- choose `c` to compress or `d` to decompress
- provide a loss value when compressing
- provide a file name

### Example compression flow

1. Start the app.
2. Enter `c`.
3. Enter a loss value such as `10`.
4. Enter a BMP filename such as `dog.bmp`.

The compressor will create `dog.bmp.qdt`.

### Example decompression flow

1. Start the app.
2. Enter `d`.
3. Enter a QDT filename such as `dog.bmp.qdt`.

The decompressor will create `dog.bmp.qdt.bmp`.

## Programmatic API

### Compress a BMP

```python
from a2main import Compressor

Compressor("dog.bmp", 10).run()
```

### Decompress a QDT

```python
from a2main import Decompressor

Decompressor("dog.bmp.qdt").run()
```

## Included Sample Assets

Verified sample BMP dimensions in this repository:

| File | Dimensions |
| --- | --- |
| `dog.bmp` | 200 × 200 |
| `toronto.bmp` | 1400 × 916 |
| `uoft.bmp` | 1024 × 1024 |

One observed run on `dog.bmp` with `loss_level = 10` produced:

- original BMP size: `120,054` bytes
- compressed QDT size: `22,714` bytes

This demonstrates the intended storage reduction, though exact results depend on image content and selected loss level.

## Architecture Details

### `a2main.py`

- validates user input filenames and loss values
- coordinates reading, compression, serialization, decompression, and saving
- converts between RGB triples and grayscale values

### `a2files.py`

- defines `BaseFile`, `BMPFile`, and `QuadTreeFile`
- parses image metadata and header bytes
- flattens output back into raw bytes for file saving
- restores quadtrees from serialized preorder data

### `a2tree.py`

- computes mean and standard deviation for image regions
- defines the quadtree node hierarchy:
  - `QuadTreeNodeEmpty`
  - `QuadTreeNodeLeaf`
  - `QuadTreeNodeInternal`
- builds and restores quadtrees
- converts quadtrees back to pixel matrices
- computes compression error with `maximum_loss`

## Validation

The repository currently contains doctests in the core modules.

Verified commands:

```bash
python -m doctest -v /tmp/workspace/mufferio/file-compression-engine/a2tree.py
python -m doctest -v /tmp/workspace/mufferio/file-compression-engine/a2files.py
```

Notes:

- `pytest` is not installed in the current environment.
- Running `python /tmp/workspace/mufferio/file-compression-engine/a2tree.py` executes doctests successfully but then fails on the optional `python_ta` import if that package is not installed.

## Current Limitations

- Compression is grayscale only; original color information is not preserved.
- Mirroring is enabled by default, so decompressed output is intentionally altered.
- The BMP reader assumes the repository's supported BMP layout and does not implement a full general-purpose BMP decoder.
- The CLI is interactive only and does not provide command-line flags.
- There is no packaging, install script, or automated CI configuration in the repository.

## Best Use Cases

- Learning how quadtree-based image compression works
- Exploring recursive spatial partitioning
- Studying binary file parsing and custom serialization in Python
- Demonstrating the tradeoff between image quality and compression strength

## Future Improvement Opportunities

- Make mirroring optional at runtime
- Preserve full RGB channels instead of forcing grayscale
- Add command-line arguments for non-interactive usage
- Expand automated tests beyond doctests
- Add support for a wider range of BMP variants
- Provide metrics such as compression ratio and reconstruction loss after each run

## License

No license file is currently present in this repository.
