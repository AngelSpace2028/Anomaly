import os
from pathlib import Path

def count_zeros_ones(data):
    ones = sum(byte.bit_count() for byte in data)
    zeros = len(data) * 8 - ones
    return zeros, ones

def print_binary_bits(data):
    """Print the binary representation of the data"""
    print(' '.join(format(byte, '08b') for byte in data))

def create_best_variation(input_file, output_dir):
    with open(input_file, 'rb') as f:
        original_data = f.read()

    base_name = Path(input_file).stem
    save_dir = os.path.join(output_dir, f"{base_name}_best_variation")
    
    if os.path.isfile(save_dir):
        print(f"Error: '{save_dir}' is a file, not a directory.")
        return 0
    
    os.makedirs(save_dir, exist_ok=True)
    
    best_score = -1
    best_data = None
    best_file_name = ""
    total_bytes = len(original_data)
    
    print(f"Input file size: {total_bytes} bytes")
    
    # Print the original data in binary
    print("\nOriginal Data (Binary):")
    print_binary_bits(original_data)

    chunk_size = 3
    max_variation = 2**24  # 2^24 variations for each 3-byte chunk
    rounds = 1  # Set to 1 for simplicity, you can adjust as needed
    
    for round_num in range(rounds):
        print(f"\n--- Round {round_num + 1} ---")
        for variation in range(max_variation):
            modified_data = bytearray(original_data)
            for i in range(0, total_bytes - chunk_size + 1, chunk_size):  # 3-byte step
                chunk = original_data[i:i+chunk_size]
                
                # Apply a transformation (e.g., XOR with the current variation)
                transformed_chunk = bytearray([b ^ (variation & 0xFF) for b in chunk])
                modified_data[i:i+chunk_size] = transformed_chunk
            
            # Calculate the imbalance of zeros and ones
            zeros, ones = count_zeros_ones(modified_data)
            score = abs(zeros - ones)
            
            if score > best_score:
                best_score = score
                best_data = bytes(modified_data)
                best_file_name = f"{base_name}_round{round_num+1}_variation{variation:08d}.bin"
                print(f"New best at round {round_num+1}, variation {variation}: 0s={zeros}, 1s={ones}, score={score}")
                
                # Print binary representation of modified data
                print(f"\nModified Data (Binary) for variation {variation}:")
                print_binary_bits(modified_data)

                # Save the best variation
                out_path = os.path.join(save_dir, best_file_name)
                with open(out_path, 'wb') as f:
                    f.write(best_data)
                print(f"Best variation saved: {out_path}")
                print(f"File size: {os.path.getsize(out_path)} bytes")
        
        print(f"Completed Round {round_num + 1}")
    
    if best_data:
        out_path = os.path.join(save_dir, best_file_name)
        with open(out_path, 'wb') as f:
            f.write(best_data)
        print(f"\nBest variation saved: {out_path}")
        print(f"File size: {os.path.getsize(out_path)} bytes")
        return 1
    
    print("No improvement found.")
    return 0

def extract_file(input_file, output_dir):
    try:
        if os.path.isfile(output_dir):
            print(f"Error: '{output_dir}' is a file, not a directory.")
            return 0
        
        os.makedirs(output_dir, exist_ok=True)

        with open(input_file, 'rb') as f:
            compressed_data = f.read()
        
        output_name = input("Enter exact output file name (with .bin extension): ").strip()
        if not output_name:
            print("No output name provided. Extraction cancelled.")
            return 0
        
        output_path = os.path.join(output_dir, output_name)
        with open(output_path, 'wb') as f:
            f.write(compressed_data)
        
        print(f"\nExtracted file saved as: {output_path}")
        print(f"File size: {os.path.getsize(output_path)} bytes")
        return 1
    
    except Exception as e:
        print(f"\nDecompression failed: {e}")
        return 0

def main():
    print("\n3-Byte Variation Evaluator with 2^24 Variations")
    print("===============================================")
    print("1. Save variation with highest 0/1 imbalance using variations")
    print("2. Extract (decompress)")
    print("3. Exit")

    choice = input("Choose option (1-3): ").strip()
    if choice == '3' or choice not in {'1', '2'}:
        print("Exiting.")
        return
    
    input_file = input("Enter input file path: ").strip()
    if not os.path.isfile(input_file):
        print("Error: File not found!")
        return
    
    output_dir = input("Enter output directory [default: current]: ").strip() or "."
    
    if choice == '1':
        result = create_best_variation(input_file, output_dir)
    elif choice == '2':
        result = extract_file(input_file, output_dir)
    
    print(f"\nTotal saved: {result}")

if __name__ == "__main__":
    main()