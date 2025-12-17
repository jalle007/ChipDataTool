"""
BER-TLV Chip Data Encoder/Decoder
Replacement for ChipDumper.exe for EMV chip data manipulation
"""

import base64
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TLVElement:
    """Represents a single TLV (Tag-Length-Value) element"""
    tag: bytes
    length: int
    value: bytes
    
    @property
    def tag_hex(self) -> str:
        """Return tag as hex string"""
        return self.tag.hex().upper()
    
    @property
    def value_hex(self) -> str:
        """Return value as hex string"""
        return self.value.hex().lower()


class ChipDataParser:
    """Main encoder/decoder class for BER-TLV chip data"""
    
    # EMV tag dictionary with descriptions
    EMV_TAGS = {
        '82': 'Application Interchange Profile (AIP)',
        '84': 'Dedicated File (DF) Name',
        '95': 'Terminal Verification Results (TVR)',
        '9A': 'Transaction Date',
        '9C': 'Transaction Type',
        '5F2A': 'Transaction Currency Code',
        '5F24': 'Application Expiration Date',
        '5F34': 'Application Primary Account Number (PAN) Sequence Number (PSN)',
        '9F02': 'Authorised Amount (Numeric)',
        '9F03': 'Amount, Other (Numeric)',
        '9F06': 'Application Identifier (AID), Terminal',
        '9F09': 'Application Version Number, Terminal',
        '9F1A': 'Terminal Country Code',
        '9F1E': 'Interface Device (IFD) Serial Number',
        '9F26': 'Application Cryptogram (AC)',
        '9F27': 'Cryptogram Information Data (CID)',
        '9F33': 'Terminal Capabilities',
        '9F34': 'Cardholder Verification Method (CVM) Results',
        '9F35': 'Terminal Type',
        '9F36': 'Application Transaction Counter (ATC)',
        '9F37': 'Unpredictable Number (UN)',
        '9F40': 'Additional Terminal Capabilities (ATC)',
        '9F41': 'Transaction Sequence Counter',
        '9F6C': 'Card Transaction Qualifiers (CTQ)',
        '9F6E': 'Form Factor Indicator (FFI)',
        '9F07': 'Application Usage Control (AUC)',
        'DF80': 'Proprietary Tag DF80',
        'DF81': 'Proprietary Tag DF81',
    }
    
    # Decode base64 chip data string to list of TLV elements
    # Args: chip_data: Base64-encoded chip data string
    # Returns: List of TLVElement objects
    # Raises: ValueError: If base64 string is invalid or TLV structure is malformed
    def decode_base64(self, chip_data: str) -> List[TLVElement]:
        try:
            # Decode base64 to bytes
            raw_bytes = base64.b64decode(chip_data)
        except Exception as e:
            raise ValueError(f"Invalid base64 input: {e}")
        
        # Check for wrapper tag 0x00 (common in some EMV implementations)
        # If present, unwrap the nested TLV data
        if len(raw_bytes) >= 2 and raw_bytes[0] == 0x00:
            wrapper_length = raw_bytes[1]
            if len(raw_bytes) >= 2 + wrapper_length:
                # Extract the nested TLV data from within the wrapper
                raw_bytes = raw_bytes[2:2 + wrapper_length]
        
        # Parse TLV structure
        return self.parse_tlv(raw_bytes)
    
    # Parse raw bytes into TLV elements
    # Args: data: Raw byte array containing TLV data
    # Returns: List of TLVElement objects
    # Raises: ValueError: If TLV structure is malformed
    def parse_tlv(self, data: bytes) -> List[TLVElement]:
        """Parse raw bytes into TLV elements"""
        elements = []
        offset = 0
        
        while offset < len(data):
            # Parse tag
            tag_start = offset
            first_byte = data[offset]
            offset += 1
            
            # Check if 2-byte tag (bits 1-5 of first byte = 11111)
            if (first_byte & 0x1F) == 0x1F:
                # 2-byte tag - need to read next byte
                if offset >= len(data):
                    raise ValueError(f"Incomplete 2-byte tag at offset {tag_start}")
                offset += 1
                tag = data[tag_start:offset]
            else:
                # 1-byte tag
                tag = data[tag_start:offset]
            
            # Parse length
            if offset >= len(data):
                raise ValueError(f"Missing length field for tag {tag.hex().upper()}")
            
            length_byte = data[offset]
            offset += 1
            
            if length_byte & 0x80:
                # Long form length - bit 7 set
                num_length_bytes = length_byte & 0x7F
                
                if num_length_bytes == 0:
                    # Indefinite length not supported
                    raise ValueError(f"Indefinite length form not supported for tag {tag.hex().upper()}")
                
                if offset + num_length_bytes > len(data):
                    raise ValueError(f"Incomplete length field for tag {tag.hex().upper()}")
                
                # Read length bytes (big-endian)
                length = 0
                for i in range(num_length_bytes):
                    length = (length << 8) | data[offset]
                    offset += 1
            else:
                # Short form length - bit 7 clear
                length = length_byte
            
            # Parse value
            if offset + length > len(data):
                raise ValueError(
                    f"Incomplete value for tag {tag.hex().upper()}, "
                    f"expected {length} bytes but only {len(data) - offset} available"
                )
            
            value = data[offset:offset + length]
            offset += length
            
            elements.append(TLVElement(tag=tag, length=length, value=value))
        
        return elements
    
    # Encode tag-hex pairs to base64 chip data string
    # Args: tags: Dictionary of tag (hex string) -> value (hex string)
    # Returns: Base64-encoded chip data string
    # Raises: ValueError: If tag or value format is invalid
    def encode_to_base64(self, tags: Dict[str, str]) -> str:
        """Encode tag-hex pairs to base64 chip data string"""
        tlv_bytes = bytearray()
        
        for tag_hex, value_hex in tags.items():
            # Build TLV for this tag
            tlv = self.build_tlv(tag_hex, value_hex)
            tlv_bytes.extend(tlv)
        
        # Encode to base64
        return base64.b64encode(bytes(tlv_bytes)).decode('ascii')
    
    # Build TLV bytes from tag and hex value
    # Args: tag_hex: Tag as hex string (e.g., '82' or '9F34')
    #       value_hex: Value as hex string (e.g., '7800')
    # Returns: Complete TLV as bytes
    # Raises: ValueError: If tag or value format is invalid
    def build_tlv(self, tag_hex: str, value_hex: str) -> bytes:
        """Build TLV bytes from tag and hex value"""
        # Remove any spaces or common separators
        tag_hex = tag_hex.replace(' ', '').replace('0x', '').upper()
        value_hex = value_hex.replace(' ', '').replace('0x', '').lower()
        
        # Validate hex strings
        try:
            tag = bytes.fromhex(tag_hex)
            value = bytes.fromhex(value_hex)
        except ValueError as e:
            raise ValueError(f"Invalid hex string: {e}")
        
        # Validate tag length (1 or 2 bytes)
        if len(tag) not in (1, 2):
            raise ValueError(f"Invalid tag length: {len(tag)} bytes (must be 1 or 2)")

        # Build length field
        value_length = len(value)
        if value_length <= 127:
            # Short form
            length_bytes = bytes([value_length])
        else:
            # Long form
            # Determine number of bytes needed for length
            length_value = value_length
            num_bytes = 0
            temp = length_value
            while temp > 0:
                num_bytes += 1
                temp >>= 8
            
            # First byte: 0x80 | num_bytes
            length_bytes = bytes([0x80 | num_bytes])
            
            # Length bytes (big-endian)
            for i in range(num_bytes - 1, -1, -1):
                length_bytes += bytes([(length_value >> (i * 8)) & 0xFF])
        
        # Combine tag + length + value
        return tag + length_bytes + value
    
    # Decode base64 chip data to dictionary of tag-hex pairs
    # Args: chip_data: Base64-encoded chip data string
    # Returns: Dictionary of tag (hex string) -> value (hex string)
    def decode_to_dict(self, chip_data: str) -> Dict[str, str]:
        """Decode base64 chip data to dictionary of tag-hex pairs"""
        elements = self.decode_base64(chip_data)
        return {elem.tag_hex: elem.value_hex for elem in elements}
    
    # Print TLV elements in human-readable format
    # Args: elements: List of TLVElement objects
    def print_readable(self, elements: List[TLVElement]) -> None:
        """Print TLV elements in human-readable format"""
        print(f"{'Tag':<8} {'Name':<50} {'Value':<20} {'Length':<6}")
        print("-" * 90)
        
        for elem in elements:
            tag = elem.tag_hex
            name = self.EMV_TAGS.get(tag, 'Unknown Tag')
            value = elem.value_hex
            length = elem.length
            
            # Truncate long values for display
            display_value = value if len(value) <= 32 else value[:32] + '...'
            
            print(f"{tag:<8} {name:<50} {display_value:<20} {length:<6}")
    
    # Print TLV elements in tab-delimited format (ready for Excel)
    # Args: elements: List of TLVElement objects
    def print_tab_delimited(self, elements: List[TLVElement]) -> None:
        """Print TLV elements in tab-delimited format (ready for Excel)"""
        # Print header
        print("Tag\tHex Value\tDescription")
        
        # Print each element as tab-delimited row
        for elem in elements:
            tag = elem.tag_hex
            value = elem.value_hex
            name = self.EMV_TAGS.get(tag, 'Unknown Tag')
            print(f"{tag}\t{value}\t{name}")
    
    # Check if CDCVM was performed (9F6C byte 2, bit 7)
    # Args: ctq_hex: Card Transaction Qualifiers hex value (e.g., '0080')
    # Returns: True if CDCVM was performed, False otherwise
    def is_cdcvm_performed(self, ctq_hex: str) -> bool:
        """Check if CDCVM was performed (9F6C byte 2, bit 7)"""
        try:
            ctq_bytes = bytes.fromhex(ctq_hex.replace('0x', ''))
            if len(ctq_bytes) < 2:
                return False
            return (ctq_bytes[1] & 0x80) == 0x80
        except ValueError:
            return False
    
    # Set CDCVM performed bit in CTQ (9F6C byte 2, bit 7)
    # Args: ctq_hex: Card Transaction Qualifiers hex value (e.g., '0000')
    # Returns: Modified CTQ hex value with CDCVM bit set (e.g., '0080')
    def set_cdcvm_bit(self, ctq_hex: str) -> str:
        """Set CDCVM performed bit in CTQ (9F6C byte 2, bit 7)"""
        ctq_bytes = bytearray.fromhex(ctq_hex.replace('0x', ''))
        
        # Ensure at least 2 bytes
        while len(ctq_bytes) < 2:
            ctq_bytes.append(0)
        
        # Set bit 7 of byte 2
        ctq_bytes[1] |= 0x80
        
        return ctq_bytes.hex().lower()
    
def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python chip_parser.py decode <base64_string> [--tab]")
        print("  python chip_parser.py encode <tag1>=<hex1> <tag2>=<hex2> ...")
        print("")
        print("Options:")
        print("  --tab    Output in tab-delimited format (ready for Excel)")
        sys.exit(1)
    
    parser = ChipDataParser()
    command = sys.argv[1].lower()
    
    if command == 'decode':
        if len(sys.argv) < 3:
            print("Error: Please provide base64 chip data string")
            sys.exit(1)
        
        # Check for --tab flag
        tab_delimited = '--tab' in sys.argv
        chip_data = sys.argv[2]
        
        try:
            elements = parser.decode_base64(chip_data)
            if tab_delimited:
                parser.print_tab_delimited(elements)
            else:
                parser.print_readable(elements)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif command == 'encode':
        if len(sys.argv) < 3:
            print("Error: Please provide tag=hex pairs")
            sys.exit(1)
        
        tags = {}
        for arg in sys.argv[2:]:
            if '=' not in arg:
                print(f"Error: Invalid format '{arg}', expected tag=hex")
                sys.exit(1)
            tag, value = arg.split('=', 1)
            tags[tag] = value
        
        try:
            chip_data = parser.encode_to_base64(tags)
            print(chip_data)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    else:
        print(f"Error: Unknown command '{command}'")
        sys.exit(1)


if __name__ == '__main__':
    main()
