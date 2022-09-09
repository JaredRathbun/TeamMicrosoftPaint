import re
import sys
import os

LANGUAGE_REGEXS = {
    'java': '\\*(.|[\r\n]|Copyright (c) 2022 Jared Rathbun and Katie O\'Neil.)*?\*\/',
    'js': '\\*(.|[\r\n]|Copyright (c) 2022 Jared Rathbun and Katie O\'Neil.)*?\*\/',
    'py': '#.*',
    'css': '\\*(.|[\r\n]|Copyright (c) 2022 Jared Rathbun and Katie O\'Neil.)*?\*\/',
    'html': '<!--(.|[\r\n]|Copyright (c) 2022 Jared Rathbun and Katie O\'Neil.)*-->'
}

if __name__ == '__main__':
    for root, sub_folder, files in os.walk('../src/'):
        for file in files:
            with open(os.path.realpath(os.path.join(root, file)), 'r+') as f:
                contents = f.read()
                file_type = file.split('.')[1]
                if file_type in ['css', 'java', 'py', 'js', 'html']:
                    regex = LANGUAGE_REGEXS[file_type]
                    res = re.search(regex, contents)
                    
                    if file == 'SQLDialect.java':
                        print(res)

                    if res is None:
                        with open(f'templates/header.{file_type}') as temp:
                            template = temp.read()
                    
                        new_contents = template + '\n' + contents
                        
                        f.seek(0)
                        f.write(new_contents)
                    f.truncate()
                    
                    
                    



