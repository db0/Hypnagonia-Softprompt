import os
import replacements as rep

input_path = r'C:\Google Drive\Projects\Hypnagonia Gdrive\softprompt\magazines\manually_processesed'
output_path =r'C:\Google Drive\Projects\Hypnagonia Gdrive\softprompt\magazines\processed'
for root, directories, file in os.walk(input_path):
    for file in file:
        if not (file.endswith(".txt")):
            continue
        output = open(os.path.join(output_path,file), "w", encoding='utf-8')
        input = open(os.path.join(root,file), encoding='utf-8')
        for line in input:
           output.write(rep.ai_training_format(line))
        input.close()
        output.close()