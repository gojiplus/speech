#!/usr/bin/env python3
# simple_pydub_fix.py
# Simple fix for pydub in Python 3.13 based on GitHub issue #725

import os
import shutil

def fix_pydub():
    """Apply a simple fix to make pydub work with Python 3.13."""
    
    # Find the pydub package location
    import pydub
    pydub_dir = os.path.dirname(pydub.__file__)
    print(f"Found pydub installation at: {pydub_dir}")
    
    # Path to utils.py
    utils_path = os.path.join(pydub_dir, "utils.py")
    
    # Create backup of original utils.py
    utils_backup = utils_path + ".backup"
    if not os.path.exists(utils_backup):
        shutil.copy2(utils_path, utils_backup)
        print(f"Created backup of utils.py at {utils_backup}")
    
    # Read the utils.py file
    with open(utils_path, "r") as f:
        content = f.read()
    
    # Check if it has the problematic import
    if "import pyaudioop as audioop" in content:
        # Replace with a try-except block
        fixed_content = content.replace(
            "import pyaudioop as audioop",
            "try:\n    import pyaudioop as audioop\nexcept ImportError:\n    import audioop"
        )
        
        # Write the fixed content
        with open(utils_path, "w") as f:
            f.write(fixed_content)
        
        print(f"Applied fix to {utils_path}")
        print("pydub should now work with Python 3.13!")
    else:
        print("File doesn't contain the expected import or might already be fixed.")

if __name__ == "__main__":
    fix_pydub()