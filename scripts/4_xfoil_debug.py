import subprocess
import os
import shutil
import sys

def test_single_airfoil():
    """
    Minimalist debug script to fix XFOIL crashing on WSL.
    """
    # 1. SETUP PATHS
    base_dir = os.getcwd()
    # Adjust this if your clean data is elsewhere
    source_dat = os.path.join(base_dir, 'airfoil_data_clean', 'naca0012.dat')
    
    # We will copy the .dat file to the current folder to simplify XFOIL's life
    local_dat = os.path.join(base_dir, 'naca0012.dat')
    
    print(f"--- DEBUG MODE ---")
    print(f"Working Directory: {base_dir}")
    print(f"Source File: {source_dat}")
    
    if not os.path.exists(source_dat):
        print("❌ Error: Source naca0012.dat not found! Run the generator script first.")
        return

    # 2. PREPARE DATA FILE (FORCE LINUX LINE ENDINGS)
    # This is critical for WSL. XFOIL chokes on Windows \r\n newlines.
    try:
        with open(source_dat, 'r') as f_in:
            content = f_in.read()
        
        # Write to local root with explicit newline='\n' (Unix format)
        with open(local_dat, 'w', newline='\n') as f_out:
            f_out.write(content)
            
        print(f"✅ Copied naca0012.dat to root (converted to Unix format)")
    except Exception as e:
        print(f"❌ File Prep Error: {e}")
        return

    # 3. CREATE INPUT SCRIPT (NO GRAPHICS)
    # We skip 'PLOP' entirely. We rely on defaults.
    # We use explicit \n to ensure commands are sent correctly.
    input_commands = (
        f"LOAD naca0012.dat\n"
        f"naca0012\n"
        f"PPAR\n"
        f"N 160\n"
        f"\n"
        f"\n"
        f"OPER\n"
        f"VISC 1000000\n"
        f"ALFA 0\n"
        f"QUIT\n"
    )

    print("\n--- Running XFOIL ---")
    
    try:
        # Run XFOIL using communicate() which is safer than file redirection
        process = subprocess.Popen(
            ['xfoil'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=base_dir
        )
        
        # Send commands and get output
        stdout, stderr = process.communicate(input=input_commands)
        
        # 4. ANALYZE OUTPUT
        print("\n=== XFOIL STDOUT (FULL) ===")
        print(stdout)
        print("===========================")
        
        if stderr:
            print("\n=== XFOIL STDERR ===")
            print(stderr)
            
        # Check if it actually loaded
        if "Point added" in stdout or "Station" in stdout or "cl =" in stdout:
            print("\n✅ SUCCESS! XFOIL ran and calculated Alpha 0.")
            print("You can now apply these fixes (newline='\\n' and removing PLOP) to your main script.")
        else:
            print("\n❌ FAILURE. XFOIL did not calculate.")
            
            if "File not found" in stdout:
                print("-> Diagnosis: XFOIL still can't see the file. Check permissions.")
            elif "Read failed" in stdout:
                print("-> Diagnosis: The .dat file format is still corrupt/bad.")
            else:
                print("-> Diagnosis: XFOIL crashed or ignored commands.")

    except FileNotFoundError:
        print("❌ CRITICAL: 'xfoil' command not found. Is it installed?")
    except Exception as e:
        print(f"❌ Python Error: {e}")

if __name__ == "__main__":
    test_single_airfoil()