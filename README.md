# BER-TLV Chip Data Encoder/Decoder

Python replacement for ChipDumper.exe for EMV chip data manipulation in payment testing.

## Features

- ✅ Decode base64 chip data to readable TLV elements
- ✅ Encode tag-hex pairs back to base64 chip data
- ✅ Support for 1-byte and 2-byte EMV tags
- ✅ Variable-length encoding (short and long form)
- ✅ Built-in EMV tag dictionary with descriptions
- ✅ CDCVM bit manipulation helpers
- ✅ Tab-delimited output for Excel/spreadsheets
- ✅ No external dependencies (Python standard library only)

## Installation

No installation required! Just Python 3.7+

```bash
# Clone or copy files
cd ChipDataTool

# Run tests
python test_chip_parser.py

# Run examples
python examples.py
```

## Quick Start

### Decode Chip Data

```python
from chip_parser import ChipDataParser

parser = ChipDataParser()

chip_data = "AKOCAngAhAegAAAAAxAQlQUA..."
elements = parser.decode_base64(chip_data)
parser.print_readable(elements)
```

### Encode Chip Data

```python
tags = {
    '82': '7800',
    '9F34': '040000',
    '9F6C': '0080',
}

chip_data = parser.encode_to_base64(tags)
print(chip_data)
```

### Modify Chip Data

```python
# Decode
tags = parser.decode_to_dict(original_chip_data)

# Modify for CDCVM test
tags['9F34'] = '040000'  # Enciphered PIN ICC
tags['9F6C'] = parser.set_cdcvm_bit(tags.get('9F6C', '0000'))

# Encode back
modified = parser.encode_to_base64(tags)
```

## CLI Usage

```bash
# Decode chip data (normal format)
python chip_parser.py decode "AKOCAngAhAeg..."

# Decode chip data (tab-delimited for Excel)
python chip_parser.py decode "AKOCAngAhAeg..." --tab

# Encode from tag-hex pairs
python chip_parser.py encode 82=7800 9F34=040000 9F6C=0080
```

## Common EMV Tags

| Tag   | Description |
|-------|-------------|
| 82    | Application Interchange Profile (AIP) |
| 9F34  | Cardholder Verification Method (CVM) Results |
| 9F6C  | Card Transaction Qualifiers (CTQ) |
| 9F6E  | Form Factor Indicator (FFI) |
| 9A    | Transaction Date |
| 9C    | Transaction Type |

## CDCVM Testing

```python
# Check if CDCVM was performed
is_cdcvm = parser.is_cdcvm_performed('0080')  # True

# Set CDCVM bit in CTQ
ctq = parser.set_cdcvm_bit('0000')  # Returns '0080'
```

## Output Formats

### Readable Format (Default)
```
Tag      Name                                               Value                Length
------------------------------------------------------------------------------------------
82       Application Interchange Profile (AIP)              7800                 2     
9F34     Cardholder Verification Method (CVM) Results       040302               3     
```

### Tab-Delimited Format (For Excel)
```
Tag	Hex Value	Description
82	7800	Application Interchange Profile (AIP)
9F34	040302	Cardholder Verification Method (CVM) Results
```

Use `--tab` flag in CLI:
```bash
python chip_parser.py decode "AKOCAngAhAeg..." --tab
```

Or in Python:
```python
parser.print_tab_delimited(elements)
```

## Running Tests

```bash
python test_chip_parser.py
```

All tests should pass with OK status.

## Examples

See `examples.py` for detailed usage examples:

1. Decoding chip data
2. Encoding chip data
3. Modifying chip data for CDCVM tests
4. Creating chip data from scratch

## Project Structure

```
ChipDataTool/
├── chip_parser.py          # Main implementation
├── test_chip_parser.py     # Unit tests
├── examples.py             # Usage examples
├── README.md              # This file
└── ChipDumper-Python-Requirements.md  # Detailed specifications
```

## License

MIT License - Free to use and modify
