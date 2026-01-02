import os
import glob

def upscale_smart(input_path, scale=4):
    """
    Upscales a map by repeating grid cells, NOT concatenating digits.
    Turns "0 3" into "0 0 0 0 3 3 3 3" (correct),
    instead of "0000 3333" (incorrect).
    """
    base_name = os.path.basename(input_path)
    name, ext = os.path.splitext(base_name)
    
    # Avoid double-scaling
    if "_highres" in name:
        return

    output_filename = f"{name}_highres{ext}"
    output_path = os.path.join(os.path.dirname(input_path), output_filename)

    with open(input_path, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # 1. Parse line into individual cell tokens
        # Assuming space or comma separation
        if ',' in line:
            delimiter = ','
        else:
            delimiter = ' ' # Default to space
            
        cells = line.split(delimiter)
        # Filter out empty strings if multiple spaces existed
        cells = [c for c in cells if c.strip()]
        
        # 2. Upscale the row horizontally
        # Repeat each cell 'scale' times
        new_row_cells = []
        for cell in cells:
            for _ in range(scale):
                new_row_cells.append(cell)
        
        # Join back into a string
        new_row_str = " ".join(new_row_cells)
        
        # 3. Upscale vertical rows
        for _ in range(scale):
            new_lines.append(new_row_str)

    with open(output_path, 'w') as f:
        for line in new_lines:
            f.write(line + "\n")
            
    print(f"✅ Fixed Upscale: {output_filename}")

def main():
    map_folder = "map"
    files = glob.glob(os.path.join(map_folder, "scenario*.txt"))
    # Exclude existing highres files from being inputs
    files = [f for f in files if "_highres" not in f]
    
    if not files:
        print("No source maps found.")
        return

    print(f"Applying Smart Upscale (Scale: 4x)...")
    for file_path in files:
        upscale_smart(file_path, scale=4)
        
    print("\nDone! Now run main.py with the new maps.")

if __name__ == "__main__":
    main()