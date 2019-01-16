from cx_Freeze import setup, Executable

base = None    

executables = [Executable("nju-login.py", base=base)]

packages = ["idna", "urllib", "json", "time", "os", "base64", "sys", "codecs"]
options = {
    'build_exe': {    
        'packages':packages,
    },    
}

setup(
    name = "nju-login",
    options = options,
    version = "1.0",
    description = '',
    executables = executables
)