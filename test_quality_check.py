#!/usr/bin/env python3
"""
Test script for data quality check functionality
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from quality_check import check_data_quality, send_error_message, send_success_message

def test_quality_check():
    """Test the data quality check functionality"""
    print("🧪 Testing data quality check functionality...")
    
    try:
        # Test quality check
        print("1. Testing data quality check...")
        quality_passed, current_nmv, last_nmv = check_data_quality()
        
        print(f"   Current NMV: {current_nmv:,.0f}")
        print(f"   Last NMV: {last_nmv:,.0f if last_nmv is not None else 'None (first run)'}")
        print(f"   Is first day of month: {datetime.now().day == 1}")
        
        if quality_passed:
            print(f"✅ Quality check passed!")
            
            # Test success message
            print("2. Testing success message...")
            send_success_message()
            print("✅ Success message sent!")
            
        else:
            print(f"❌ Quality check failed!")
            
            # Test error message
            print("2. Testing error message...")
            send_error_message(current_nmv, last_nmv)
            print("✅ Error message sent!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_quality_check()
