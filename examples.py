"""
Usage examples for chip_parser
"""

from chip_parser import ChipDataParser


def example_decode():
    """Example: Decode chip data"""
    print("=" * 80)
    print("Example 1: Decode Chip Data")
    print("=" * 80)
    
    parser = ChipDataParser()
    
    # Real chip data from test
    chip_data = "AKOCAngAhAegAAAAAxAQlQUAESIzRJoDGRIRnAEAXyoCCEBfJAMiEjFfNAEBnwIGAAAAAAUAnwMGAAAAAAAAnwYHoAAAAAMQEJ8JAgCWnxoCCECfHghQVDAxMDA0NJ8mCL2tYGAB3sounycBgJ8zA+D4yJ80AwQDAp81ASKfNgIAA583BEdyYEmfQAXwAPCgAZ9BBAAAAXWfBwL/AN+AAQDfgQEC"
    
    elements = parser.decode_base64(chip_data)
    parser.print_readable(elements)
    print()


def example_encode():
    """Example: Encode chip data"""
    print("=" * 80)
    print("Example 2: Encode Chip Data")
    print("=" * 80)
    
    parser = ChipDataParser()
    
    # Create chip data for CDCVM test
    tags = {
        '82': '7800',
        '9F34': '040000',  # Enciphered PIN ICC
        '9F6C': '0080',    # CDCVM performed
        '9A': '250115',
        '9C': '00',
    }
    
    chip_data = parser.encode_to_base64(tags)
    print(f"Encoded chip data: {chip_data}")
    print()


def example_modify_chip_data():
    """Example: Modify existing chip data"""
    print("=" * 80)
    print("Example 3: Modify Chip Data for CDCVM Test")
    print("=" * 80)
    
    parser = ChipDataParser()
    
    # Start with existing chip data
    original = "AKOCAngAhAegAAAAAxAQlQUAESIzRJoDGRIRnAEAXyoCCEBfJAMiEjFfNAEBnwIGAAAAAAUAnwMGAAAAAAAAnwYHoAAAAAMQEJ8JAgCWnxoCCECfHghQVDAxMDA0NJ8mCL2tYGAB3sounycBgJ8zA+D4yJ80AwQDAp81ASKfNgIAA583BEdyYEmfQAXwAPCgAZ9BBAAAAXWfBwL/AN+AAQDfgQEC"
    
    # Decode to dictionary
    tags = parser.decode_to_dict(original)
    
    print("Original CVM Results (9F34):", tags.get('9F34', 'Not present'))
    print("Original CTQ (9F6C):", tags.get('9F6C', 'Not present'))
    
    # Modify for CDCVM scenario
    tags['9F34'] = '040000'  # Enciphered PIN ICC
    
    # Set CDCVM bit if CTQ exists
    if '9F6C' in tags:
        tags['9F6C'] = parser.set_cdcvm_bit(tags['9F6C'])
    else:
        tags['9F6C'] = '0080'
    
    print("\nModified CVM Results (9F34):", tags['9F34'])
    print("Modified CTQ (9F6C):", tags['9F6C'])
    print("CDCVM performed?", parser.is_cdcvm_performed(tags['9F6C']))
    
    # Encode back
    modified = parser.encode_to_base64(tags)
    print(f"\nModified chip data: {modified[:60]}...")
    print()


def example_create_from_scratch():
    """Example: Create chip data from scratch"""
    print("=" * 80)
    print("Example 4: Create Chip Data from Scratch")
    print("=" * 80)
    
    parser = ChipDataParser()
    
    # Define all required tags
    cdcvm_tags = {
        '82': '7800',              # AIP
        '84': 'a0000000031010',    # AID
        '95': '0011223344',        # TVR
        '9A': '250115',            # Transaction Date
        '9C': '00',                # Transaction Type
        '5F2A': '0840',            # Currency (USD)
        '9F02': '000000000500',    # Amount
        '9F34': '040000',          # CVM Results (Enciphered PIN)
        '9F6C': '0080',            # CTQ (CDCVM)
    }
    
    chip_data = parser.encode_to_base64(cdcvm_tags)
    print(f"Created chip data: {chip_data}")
    
    # Verify by decoding
    print("\nVerification (decode back):")
    elements = parser.decode_base64(chip_data)
    parser.print_readable(elements)
    print()


if __name__ == '__main__':
    example_decode()
    example_encode()
    example_modify_chip_data()
    example_create_from_scratch()
