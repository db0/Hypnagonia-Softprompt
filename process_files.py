import os
import replacements as rep

input_path = r'C:\Google Drive\Projects\Hypnagonia Gdrive\softprompt\books\manually_processed'
output_path =r'C:\Google Drive\Projects\Hypnagonia Gdrive\softprompt\books\processed'
for root, directories, file in os.walk(input_path):
    for file in file:
        print(file)
        if not (file.endswith(".txt")):
            continue
        output = open(os.path.join(output_path,file), "w", encoding='utf-8')
        input = open(os.path.join(root,file), encoding='utf-8')
        for line in input:
           output.write(rep.ai_training_format(line))
        output.write('<|endoftext|>')
        input.close()
        output.close()