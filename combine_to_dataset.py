import os

input_paths = [
    'C:\Projects\SubredditScraper\output',
    'C:\Google Drive\Projects\Hypnagonia Gdrive\softprompt\magazines\processed',
    'C:\Google Drive\Projects\Hypnagonia Gdrive\softprompt\\books\processed',
]
output_file =r'C:\Google Drive\Projects\Hypnagonia Gdrive\softprompt\dataset\dataset.txt'
output = open(output_file, "w", encoding='utf-8')
for input_path in input_paths:
    print(f"Processing: {input_path}")
    for root, directories, file in os.walk(input_path):
        for file in file:
            # print(file)
            if not (file.endswith(".txt")):
                continue
            input = open(os.path.join(root,file), encoding='utf-8')
            try:
                for line in input:
                    output.write(line)
            # except UnicodeDecodeError:
            except UnicodeEncodeError:
                print(f"failed to parse line: {line}")
            input.close()
output.close()