"""
Debug script to analyze chip data structure
"""

import base64
from chip_parser import ChipDataParser

# The problematic chip data from CSV
chip_data = "AKOCAngAhAegAAAAAxAQlQUAESIzRJoDGRIRnAEAXyoCCEBfJAMiEjFfNAEBnwIGAAAAAAUAnwMGAAAAAAAAnwYHoAAAAAMQEJ8JAgCWnxoCCECfHghQVDAxMDA0NJ8mCL2tYGAB3sounycBgJ8zA+D4yJ80AwQDAp81ASKfNgIAA583BEdyYEmfQAXwAPCgAZ9BBAAAAXWfBwL/AN+AAQDfgQEC"

print("Chip Data Decoder Debug")
print("=" * 80)

parser = ChipDataParser()

try:
    raw_bytes = base64.b64decode(chip_data)
    print(f"Successfully decoded base64: {len(raw_bytes)} bytes\n")
    
    # Use debug parser
    parser.debug_parse_tlv(raw_bytes)
    
    print("\n" + "=" * 80)
    print("Attempting full parse...")
    elements = parser.parse_tlv(raw_bytes)
    
    print(f"✓ Successfully parsed {len(elements)} TLV elements")
    parser.print_readable(elements)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
