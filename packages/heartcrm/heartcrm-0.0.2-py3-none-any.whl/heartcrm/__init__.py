import subprocess

def get_version():
    out = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0'])
    version = out.decode('utf-8').strip()
    return version

__version__ = get_version()
