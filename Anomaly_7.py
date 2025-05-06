import os
import re
from pathlib import Path

def count_zeros_ones(data):
    ones = sum(byte.bit_count() for byte in data)
    zeros = len(data) * 8 - ones
    return zeros, ones

def create_best_two_byte_variation(input_file, output_dir):
    with open(input_file, 'rb') as f:
        original_data = f.read()

    base_name = Path(input_file).stem
    save_dir = os.path.join(output_dir, f"{base_name}_2byte_variations")

    if os.path.isfile(save_dir):
        print(f"Error: '{save_dir}' is a file, not a directory.")
        return 0
    os.makedirs(save_dir, exist_ok=True)

    best_score = -1
    total_bytes = len(original_data)
    saved = 0

    print("Evaluating 2-byte XOR variations (0 to 65535)...")

    for i in range(0, total_bytes - 1):
        orig_pair = original_data[i:i+2]
        if len(orig_pair) < 2:
            continue
        orig_value = int.from_bytes(orig_pair, byteorder='big')

        for xor_val in range(65536):
            modified_data = bytearray(original_data)
            new_val = orig_value ^ xor_val
            modified_data[i:i+2] = new_val.to_bytes(2, byteorder='big')

            zeros, ones = count_zeros_ones(modified_data)
            score = abs(zeros - ones)

            if score > best_score:
                best_score = score
                score_str = f"{score:010d}"
                out_filename = f"{base_name}_pos{i:04d}_xor{xor_val:05d}_score{score_str}.bin"
                out_path = os.path.join(save_dir, out_filename)
                with open(out_path, 'wb') as f:
                    f.write(modified_data)
                print(f"Saved: {out_filename} | 0s={zeros}, 1s={ones}, score={score}")
                saved += 1

    if saved == 0:
        print("No improvements found.")
    else:
        print(f"\nTotal variations saved: {saved}")
    return saved

def extract_original_from_bin(modified_file, output_dir):
    filename = os.path.basename(modified_file)
    match = re.search(r'_pos(\d{4})_xor(\d{5})', filename)
    if not match:
        print("Filename does not contain position and xor info.")
        return 0

    pos = int(match.group(1))
    xor_val = int(match.group(2))

    with open(modified_file, 'rb') as f:
        mod_data = bytearray(f.read())

    if pos < 0 or pos + 2 > len(mod_data):
        print("Invalid XOR position.")
        return 0

    xor_bytes = int.from_bytes(mod_data[pos:pos+2], 'big') ^ xor_val
    mod_data[pos:pos+2] = xor_bytes.to_bytes(2, 'big')

    output_name = input("Enter name for the restored output file (with .bin): ").strip()
    if not output_name:
        print("No output name provided. Extraction cancelled.")
        return 0

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, output_name)
    with open(out_path, 'wb') as f:
        f.write(mod_data)

    print(f"Restored file saved as: {out_path}")
    return 1

def main():
    print("\n2-Byte XOR Variation Evaluator")
    print("==============================")
    print("1. Save every improved variation")
    print("2. Extract original file using modified .bin files")
    print("3. Exit")

    choice = input("Choose option (1-3): ").strip()
    if choice == '1':
        input_file = input("Enter input file path: ").strip()
        if not os.path.isfile(input_file):
            print("Error: File not found!")
            return
        output_dir = input("Enter output directory [default: current]: ").strip() or "."
        create_best_two_byte_variation(input_file, output_dir)

    elif choice == '2':
        input_file = input("Enter input .bin file path: ").strip()
        if not os.path.isfile(input_file):
            print("Error: File not found!")
            return
        output_dir = input("Enter output directory [default: current]: ").strip() or "."
        extract_original_from_bin(input_file, output_dir)

    else:
        print("Exiting.")

if __name__ == "__main__":
    main()