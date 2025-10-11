import json

def format_file():
    with open('temp.txt', 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    if len(lines) % 4 != 0:
        exit("Error: The number of lines in temp.txt is not a multiple of 4.")
    
    groups = [lines[i:i+4] for i in range(0, len(lines), 4)]
    
    output_lines = []
    for i, group in enumerate(groups):
        group_str = json.dumps(group, ensure_ascii=False)
        line = f"    {group_str}{',' if i < len(groups) - 1 else ''}"
        output_lines.append(line)
    
    with open('temp.json', 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines))

if __name__ == '__main__':
    format_file()