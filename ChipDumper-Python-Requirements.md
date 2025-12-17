# BER-TLV Chip Data Encoder/Decoder - Python Implementation Requirements

## Project Goal
Build a Python replacement for ChipDumper.exe that can encode/decode EMV chip data in BER-TLV format for payment testing.

## Functional Requirements

### 1. Decoder Functionality
**Input**: Base64-encoded chip data string
**Output**: Dictionary/list of tag-hex pairs

**Must support:**
- Parse BER-TLV structure from base64 input
- Handle 1-byte tags (e.g., `82`, `9A`, `9C`)
- Handle 2-byte tags (e.g., `9F34`, `9F6C`, `5F2A`)
- Handle variable-length length fields (1-3 bytes)
- Extract tag, length, and value for each TLV element
- Display output in human-readable format:
  ```
  Tag    Hex Value    Length    Description
  82     7800         2         Application Interchange Profile
  9F34   040000       3         CVM Results
  ```

### 2. Encoder Functionality
**Input**: Dictionary/list of tag-hex pairs
**Output**: Base64-encoded chip data string

**Must support:**
- Accept tag-hex pairs as input (dict or key-value format)
- Construct proper BER-TLV structure:
  - Encode tag (1 or 2 bytes)
  - Calculate and encode length field
  - Append value bytes
- Concatenate all TLV elements
- Base64-encode the final byte array

### 3. Tag Management
**Must support:**
- Predefined EMV tag dictionary with descriptions:
  ```python
  EMV_TAGS = {
      '82': 'Application Interchange Profile (AIP)',
      '9F34': 'Cardholder Verification Method (CVM) Results',
      '9F6C': 'Card Transaction Qualifiers (CTQ)',
      # ... other common tags
  }
  ```
- Lookup tag descriptions for decoder output
- Handle unknown tags (display hex without description)

### 4. Validation
**Must validate:**
- Input base64 string is valid
- Tag format is correct (1 or 2 bytes)
- Length field matches actual value length
- Hex values are valid hexadecimal

**Error handling:**
- Invalid base64 input
- Malformed TLV structure
- Tag/length/value mismatch
- Invalid hex characters

## Technical Requirements

### Core Dependencies
```python
# Standard library only (no external dependencies)
import base64          # For base64 encoding/decoding
import struct          # For byte packing/unpacking
from typing import Dict, List, Tuple, Optional
```

### BER-TLV Encoding Rules (ISO/IEC 8825-1)

**Tag Encoding:**
- **1-byte tags**: First bit (MSB) = 0
  - Example: `82` = 10000010
- **2-byte tags**: First bit (MSB) = 1, continuation follows
  - Example: `9F 34` = 10011111 00110100

**Length Encoding:**
- **Short form** (0-127 bytes): Single byte, MSB = 0
  - Example: `03` = 3 bytes follow
- **Long form** (128+ bytes): First byte MSB = 1, remaining bits = number of length bytes
  - Example: `81 FF` = 1 length byte follows, value = 255

**Value:**
- Raw bytes, length specified by length field

### Data Structures

```python
class TLVElement:
    """Represents a single TLV element"""
    tag: bytes           # 1 or 2 bytes
    length: int          # Calculated from length field
    value: bytes         # Raw value bytes

class ChipDataParser:
    """Main encoder/decoder class"""

    def decode_base64(self, chip_data: str) -> List[TLVElement]:
        """Decode base64 chip data to TLV elements"""
        pass

    def encode_to_base64(self, elements: Dict[str, str]) -> str:
        """Encode tag-hex pairs to base64 chip data"""
        pass

    def parse_tlv(self, data: bytes) -> List[TLVElement]:
        """Parse raw bytes into TLV elements"""
        pass

    def build_tlv(self, tag: str, value: str) -> bytes:
        """Build TLV bytes from tag and hex value"""
        pass
```

## Input/Output Formats

### Decoder Input
```python
# Base64 string (from test script)
chip_data = "AKOCAngAhAegAAAAAxAQlQUAESIzRJoDGRIRnAEAXyoCCEBfJAMiEjFfNAEB..."
```

### Decoder Output
```python
# Option 1: Dictionary
{
    '82': '7800',
    '9F34': '040302',
    '9F6C': '0080',
    # ...
}

# Option 2: List of tuples with descriptions
[
    ('82', '7800', 'Application Interchange Profile'),
    ('9F34', '040302', 'CVM Results'),
    ('9F6C', '0080', 'Card Transaction Qualifiers'),
]
```

### Encoder Input
```python
# Dictionary of tag-hex pairs
chip_tags = {
    '82': '7800',
    '9F34': '040000',
    '9F6C': '0080',
    '9A': '191211',
    '9C': '00',
}
```

### Encoder Output
```python
# Base64 string ready for test script
"AKOCAngAhAegAAAAAxAQlQUAESIzRJoDGRIRnwcEAACA..."
```

## Use Cases

### Use Case 1: Decode Existing Chip Data
```python
parser = ChipDataParser()
elements = parser.decode_base64(chip_data_from_test)
parser.print_readable(elements)
```

### Use Case 2: Modify Chip Data for CDCVM Test
```python
# Decode existing chip data
tags = parser.decode_to_dict(existing_chip_data)

# Modify for CDCVM scenario
tags['9F34'] = '040000'  # Enciphered PIN ICC
tags['9F6C'] = '0080'    # CDCVM performed (bit 7 set)

# Encode back to base64
new_chip_data = parser.encode_to_base64(tags)
```

### Use Case 3: Create Chip Data from Scratch
```python
cdcvm_tags = {
    '82': '7800',       # AIP
    '9F34': '040000',   # CVM Results
    '9F6C': '0080',     # CTQ (CDCVM)
    '9A': '250115',     # Transaction Date
    '9C': '00',         # Transaction Type
}

chip_data = parser.encode_to_base64(cdcvm_tags)
```

## Testing Requirements

### Unit Tests
```python
def test_decode_simple_tag():
    """Test decoding 1-byte tag"""
    # Input: 82 02 78 00
    # Expected: tag=82, length=2, value=7800

def test_decode_two_byte_tag():
    """Test decoding 2-byte tag"""
    # Input: 9F 34 03 04 03 02
    # Expected: tag=9F34, length=3, value=040302

def test_encode_decode_roundtrip():
    """Ensure encode→decode returns original data"""

def test_cdcvm_bit_flag():
    """Verify CDCVM bit 7 detection in 9F6C tag"""
    # 9F6C = 00 80 should have bit 7 set in byte 2
```

### Integration Tests
```python
def test_with_real_chip_data():
    """Test with actual chip data from CSV file"""
    # Use examples from Chip Data Encoder-Decoder.csv

def test_cdcvm_scenario():
    """Create chip data for CDCVM test case"""
    # Match requirements from todo.md CDCVM section
```

## Implementation Phases

### Phase 1: Core TLV Parser (MVP)
- Decode base64 to TLV elements
- Parse 1-byte and 2-byte tags
- Handle short-form length fields
- Basic validation

### Phase 2: Encoder
- Build TLV from tag-hex pairs
- Encode to base64
- Round-trip testing (decode→encode→decode)

### Phase 3: EMV Tag Dictionary
- Add common EMV tag descriptions
- Pretty-print decoder output

### Phase 4: CLI Interface
```bash
# Decode mode
python chip_parser.py decode --input <base64_string>
python chip_parser.py decode --file test_chip_data.txt

# Encode mode
python chip_parser.py encode --tags "82=7800,9F34=040000,9F6C=0080"
python chip_parser.py encode --file tags.json

# Interactive mode
python chip_parser.py interactive
```

### Phase 5: GUI (Optional)
- Simple tkinter/PyQt interface
- Text input for base64 decode
- Table for tag editing
- Encode button

## Reference Data

### Test Data Sources
1. `Chip Data Encoder-Decoder.csv` - Example chip data
2. Existing test scripts - Real chip data variables
3. EMVCo specifications - Tag definitions

### Key EMV Tags for Testing
```python
COMMON_EMV_TAGS = {
    '82': ('AIP', 2),              # Application Interchange Profile
    '9F34': ('CVM Results', 3),    # CVM Results
    '9F6C': ('CTQ', 2),            # Card Transaction Qualifiers
    '9F6E': ('Form Factor', 3),    # Form Factor Indicator
    '9F70': ('Protected Data', 1), # Protected Data Envelope
    '9A': ('Trans Date', 3),       # Transaction Date YYMMDD
    '9C': ('Trans Type', 1),       # Transaction Type
    '5F2A': ('Currency', 2),       # Transaction Currency Code
}
```

### CDCVM Bit Manipulation
```python
def is_cdcvm_performed(ctq_bytes: bytes) -> bool:
    """Check if CDCVM performed (9F6C byte 2, bit 7)"""
    if len(ctq_bytes) < 2:
        return False
    return (ctq_bytes[1] & 0x80) == 0x80

def set_cdcvm_bit(ctq_bytes: bytes) -> bytes:
    """Set CDCVM performed bit"""
    ctq = bytearray(ctq_bytes)
    if len(ctq) >= 2:
        ctq[1] |= 0x80  # Set bit 7
    return bytes(ctq)
```

## Success Criteria

✅ Can decode all chip data examples from CSV file
✅ Encoder output matches ChipDumper.exe output
✅ Round-trip encode/decode produces identical data
✅ Can create CDCVM test chip data matching requirements
✅ Handles all tag types from real test scripts
✅ Clear error messages for invalid input
✅ No external dependencies (standard library only)

## Future Enhancements

- JSON import/export for tag sets
- Batch processing for multiple chip data strings
- Diff mode (compare two chip data strings)
- Template system for common test scenarios
- Integration with test script DSL generator
- Web interface (Flask/FastAPI)

---

**Note**: This tool must produce byte-identical output to ChipDumper.exe for compatibility with existing test infrastructure.
