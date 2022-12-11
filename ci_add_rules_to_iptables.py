import subprocess
import re

def read_from_file_and_run():
    f1 = open(".ci_input.txt", "r")
    f1_content = f1.readlines()
    f1.close()
    for line in f1_content:
        if not '#' in line:
            sline = re.sub('\n', '', line)
            cmd = sline.split(' ')
            cmd.insert(0, 'sudo')
            subprocess.run(cmd)

if __name__ == '__main__':
    read_from_file_and_run()
