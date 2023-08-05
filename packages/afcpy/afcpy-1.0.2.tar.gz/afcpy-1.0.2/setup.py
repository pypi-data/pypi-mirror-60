import os
import fnmatch
from setuptools import find_packages, setup
from setuptools.command.build_py import build_py as build_py_orig

# modules to exclude
excluded = ['afcpy/myutils.py']

class build_py(build_py_orig):
    """
    determines which modules to include or exclude
    
    source: https://stackoverflow.com/questions/35115892/how-to-exclude-a-single-file-from-package-with-setuptools-and-setup-py
    """
    
    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)
        return [(pkg, mod, file) for (pkg, mod, file) in modules if not any(fnmatch.fnmatchcase(file, pat=pattern) for pattern in excluded)]
        
def generate_manifest():
    """
    generates the manifest file
    """
    
    pkg_dir = os.path.abspath(find_packages()[0])
    data_dir = os.path.join(pkg_dir,'data')
    data_files = []
    
    for root,folders,files in os.walk(data_dir):
        for file in files:
            afp = os.path.join(root,file)
            rfp = 'afcpy/data'+afp.split('afcpy/data')[-1]
            if file.startswith('tb'):
                data_files.append(rfp)
            elif file == 'log.xlsx':
                log_file = rfp
            else:
                continue
            
    src_dir = os.path.dirname(os.path.abspath(find_packages()[0]))
    manifest = os.path.join(src_dir,'MANIFEST.in')
    
    with open(manifest,'w') as fopen:
        for data_file in data_files:
            fopen.write('include {}\n'.format(data_file))
        fopen.write('include {}\n'.format(log_file))

def collect_dependencies():
    """
    collects the dependencies from the requirements.txt file
    """
    
    pkg_dir = os.path.abspath(find_packages()[0])
    git_dir = os.path.dirname(pkg_dir)
    req_file = os.path.join(git_dir,'requirements.txt')
    
    with open(req_file) as req_file_open:
        dependencies = [line.rstrip('\n') for line in req_file_open.readlines()]
    
    return dependencies

# generate the manifest
generate_manifest()
        
# collect the dependencies
dependencies = collect_dependencies()        

# run setup
setup(name='afcpy',
      version="1.0.2",
      author='Josh Hunt',
      author_email='hunt.brian.joshua@gmail.com',
      description="",
      url="https://github.com/jbhunt/afcpy",
      cmdclass={'build_py': build_py},
      packages=find_packages(),
      include_package_data=True,
      install_requires=dependencies,
      classifiers=["Programming Language :: Python :: 3",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   ],
      )
