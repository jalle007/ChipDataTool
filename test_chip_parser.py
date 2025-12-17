"""
Unit tests for chip_parser module
"""

import unittest
from chip_parser import ChipDataParser, TLVElement


class TestChipDataParser(unittest.TestCase):
    """Test cases for ChipDataParser"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = ChipDataParser()
    
    def test_decode_simple_tag(self):
        """Test decoding 1-byte tag"""
        # Tag 82, Length 02, Value 7800
        data = bytes.fromhex('82027800')
        elements = self.parser.parse_tlv(data)
        
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0].tag_hex, '82')
        self.assertEqual(elements[0].length, 2)
        self.assertEqual(elements[0].value_hex, '7800')
    
    def test_decode_two_byte_tag(self):
        """Test decoding 2-byte tag"""
        # Tag 9F34, Length 03, Value 040302
        data = bytes.fromhex('9F34 03 040302'.replace(' ', ''))
        elements = self.parser.parse_tlv(data)
        
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0].tag_hex, '9F34')
        self.assertEqual(elements[0].length, 3)
        self.assertEqual(elements[0].value_hex, '040302')
    
    def test_encode_simple_tag(self):
        """Test encoding 1-byte tag"""
        tlv = self.parser.build_tlv('82', '7800')
        expected = bytes.fromhex('82027800')
        self.assertEqual(tlv, expected)
    
    def test_encode_two_byte_tag(self):
        """Test encoding 2-byte tag"""
        tlv = self.parser.build_tlv('9F34', '040302')
        expected = bytes.fromhex('9F3403040302')
        self.assertEqual(tlv, expected)
    
    def test_encode_decode_roundtrip(self):
        """Test encode→decode returns original data"""
        original_tags = {
            '82': '7800',
            '9F34': '040302',
            '9A': '191211',
            '9C': '00',
        }
        
        # Encode
        chip_data = self.parser.encode_to_base64(original_tags)
        
        # Decode
        decoded_tags = self.parser.decode_to_dict(chip_data)
        
        # Compare
        self.assertEqual(decoded_tags, original_tags)
    
    def test_cdcvm_bit_detection(self):
        """Test CDCVM bit 7 detection in 9F6C tag"""
        # CDCVM performed (bit 7 set in byte 2)
        self.assertTrue(self.parser.is_cdcvm_performed('0080'))
        
        # CDCVM not performed
        self.assertFalse(self.parser.is_cdcvm_performed('0000'))
    
    def test_cdcvm_bit_setting(self):
        """Test setting CDCVM bit"""
        result = self.parser.set_cdcvm_bit('0000')
        self.assertEqual(result, '0080')
        
        # Already set should remain set
        result = self.parser.set_cdcvm_bit('0080')
        self.assertEqual(result, '0080')
    
    def test_real_chip_data(self):
        """Test with real chip data from CSV"""
        # From Chip Data Encoder-Decoder.csv
        chip_data = "AKOCAngAhAegAAAAAxAQlQUAESIzRJoDGRIRnAEAXyoCCEBfJAMiEjFfNAEBnwIGAAAAAAUAnwMGAAAAAAAAnwYHoAAAAAMQEJ8JAgCWnxoCCECfHghQVDAxMDA0NJ8mCL2tYGAB3sounycBgJ8zA+D4yJ80AwQDAp81ASKfNgIAA583BEdyYEmfQAXwAPCgAZ9BBAAAAXWfBwL/AN+AAQDfgQEC"
        
        try:
            # Decode
            elements = self.parser.decode_base64(chip_data)
            
            # Verify we got elements
            self.assertGreater(len(elements), 0)
            
            # Verify some known tags from CSV
            tags_dict = {elem.tag_hex: elem.value_hex for elem in elements}
            
            # Check key tags exist and have correct values
            self.assertIn('82', tags_dict)
            self.assertEqual(tags_dict['82'], '7800')
            
            self.assertIn('9F34', tags_dict)
            self.assertEqual(tags_dict['9F34'], '040302')
            
            self.assertIn('9A', tags_dict)
            self.assertEqual(tags_dict['9A'], '191211')
            
            # Verify we can encode it back
            chip_data_reencoded = self.parser.encode_to_base64(tags_dict)
            
            # Decode again to verify round-trip
            elements_reencoded = self.parser.decode_base64(chip_data_reencoded)
            tags_dict_reencoded = {elem.tag_hex: elem.value_hex for elem in elements_reencoded}
            
            # Should have same tags
            self.assertEqual(tags_dict, tags_dict_reencoded)
            
        except ValueError as e:
            # If parsing fails, print debug info
            import base64
            raw_bytes = base64.b64decode(chip_data)
            print(f"\nDebug info for test_real_chip_data failure:")
            print(f"Chip data length: {len(chip_data)} chars")
            print(f"Raw bytes length: {len(raw_bytes)} bytes")
            print(f"First 20 bytes (hex): {raw_bytes[:20].hex()}")
            print(f"Error: {e}")
            raise
    
    def test_invalid_base64(self):
        """Test error handling for invalid base64"""
        with self.assertRaises(ValueError):
            self.parser.decode_base64('!!!invalid!!!')
    
    def test_invalid_hex(self):
        """Test error handling for invalid hex"""
        with self.assertRaises(ValueError):
            self.parser.build_tlv('82', 'ZZZZ')
    
    def test_long_form_length(self):
        """Test encoding with long-form length (>127 bytes)"""
        # Create value with 200 bytes
        long_value = 'FF' * 200
        tlv = self.parser.build_tlv('9F34', long_value)
        
        # Parse it back
        elements = self.parser.parse_tlv(tlv)
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0].length, 200)
        self.assertEqual(elements[0].value_hex, long_value.lower())


if __name__ == '__main__':
    unittest.main()
