"""
PROJECT SETUP SCRIPT
====================

Run this script first to create all necessary folders for the project.

USAGE:
    python setup_project.py
"""

import os

def create_directory(path, description):
    """Create a directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✓ Created: {path:20s} - {description}")
    else:
        print(f"○ Exists:  {path:20s} - {description}")

def main():
    print("="*60)
    print("E-COMMERCE ANALYTICS PROJECT SETUP")
    print("="*60)
    print("\nCreating project structure...\n")
    
    # Create all necessary directories
    directories = [
        ('raw_data', 'Raw CSV input files'),
        ('aggregated_data', 'Processed summary files'),
        ('logs', 'Processing logs'),
        ('data', 'Streamlit dashboard data folder'),
        ('pages', 'Additional Streamlit dashboard pages'),
    ]
    
    for directory, description in directories:
        create_directory(directory, description)
    
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Generate sample data:")
    print("   python generate_sample_data.py")
    print("\n2. Process the data:")
    print("   python ecommerce_data_processor.py")
    print("\n3. Run Streamlit dashboard:")
    print("   streamlit run app.py")
    print("="*60)

if __name__ == "__main__":
    main()
