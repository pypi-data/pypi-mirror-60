import sys
import os
import platform
import shutil
import multiprocessing
import colorama
from pathlib import Path
from lockfile import LockFile
import argparse

class term_colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

TCIA = term_colors.WARNING+"[cia] "+term_colors.ENDC
class PackageError(Exception):
    def __init__(self,msg=''):
        self.msg = msg
    
    def print_error(self):
        print(self.msg)


class Package:
    git_exe = 'git'
    cmake_exe = 'cmake'
    cmake_path = ''

    def __init__(self,name):
        self.name = name
        self.path = Path(os.path.expanduser("~/ciavelli_packages/"+name))
        self.clone_path = str(self.path/"git_clone")
        self.install_path = str(self.path/"install")
        self.build_cache_path = str(self.path/"ciavelli_build")
        self.lock_file_path = str(self.path/".."/name)
        self.info_file_path = str(self.path/"info.json")
  
        #Make sure the path exists for lock files cloning etc.
        self.lockfile = LockFile(self.lock_file_path)

    def remove_project(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
        return 0

    def update(self):
        if os.path.exists(self.clone_path):
            #Ok the project already exists try to update the project then

            #If the project already exists it means that the clone was succesfull.
            if execute_command("cd "+self.clone_path+"&&"+ Package.git_exe+" pull") != 0:
                raise PackageError(TCIA+term_colors.FAIL+"Could not pull changes from upstream. Unable to update "+term_colors.HEADER+self.package+term_colors.ENDC)

            print(TCIA+term_colors.GREEN+"Successfully fetched upstream changes for package "+term_colors.HEADER+self.name+term_colors.ENDC)
            return 0
        else:
            raise PackageError(TCIA+term_colors.FAIL+"Cannot update package "+term_colors.HEADER+self.name+term_colors.FAIL+". Package does not exist...")

    def download_using_git(self,url='',commit='',branch=''):
        if self.is_downloaded():
            raise PackageError(TCIA+term_colors.FAIL+"The project is already downloaded. If you really want to use this command use Package.remove_project() first.")
        
        if branch != '' and commit != '':
            self.remove_project()
            raise PackageError(TCIA+term_colors.FAIL+"A commit is unique it does not make sense to define a branch and a commit, either specify branch or commit")
            
        if url == '':
            raise PackageError(TCIA+term_colors.FAIL+"The package "+term_colors.HEADER+self.name+term_colors.ENDC+" does not exist and no url was provided!")

        os.makedirs(self.path,exist_ok=True)
        if execute_command(Package.git_exe+' clone '+url+' '+self.clone_path) != 0:
            self.remove_project()
            raise PackageError(TCIA+term_colors.FAIL+"Could not clone project from url "+term_colors.HEADER+url+term_colors.FAIL+". Check if you are connected to the internet and try again.")
            
        print(TCIA+term_colors.GREEN+"Successfully cloned the project "+term_colors.HEADER+self.name+term_colors.GREEN+" from "+url+term_colors.ENDC)
            
        if branch != '' or commit != '':
            if execute_command('cd '+self.clone_path+"&&"+Package.git_exe+" checkout "+commit+branch) != 0:
                self.remove_project()
                raise PackageError(TCIA+term_colors.FAIL+"Could not checkout commit/branch "+term_colors.HEADER+commit+branch+term_colors.FAIL+". Check if this branch/commit does exist")
            print(TCIA+term_colors.GREEN+"Successfully checked out branch/commit "+commit+branch+" in package "+term_colors.HEADER+self.name+term_colors.ENDC)
        return 0
    
    def is_installed(self):
        return os.path.isfile(self.path/"info.json")
    
    def is_downloaded(self):
        return os.path.isdir(self.clone_path)
    
    def getName(self):
        return self.name
    def get_lockfile(self):
        return self.lockfile

    def build(self,install_path=''):
        if install_path == '':
            install_path = self.install_path
        os.makedirs(self.build_cache_path,exist_ok=True)
        if execute_command("cd "+self.build_cache_path+'&&'+Package.cmake_exe+" "+self.clone_path+" -DCMAKE_PREFIX_PATH=\""+Package.cmake_path+"\" -DCMAKE_INSTALL_PREFIX="+install_path+" &&"+Package.cmake_exe+" --build . -j"+str(multiprocessing.cpu_count())) != 0:
            raise PackageError(TCIA+term_colors.FAIL+"Could not install the package "+term_colors.HEADER+self.name+term_colors.ENDC)
        return 0

    def install(self):
        if execute_command("cd "+self.build_cache_path+'&&'+Package.cmake_exe+" --install .") != 0:
            raise PackageError(TCIA+term_colors.FAIL+"Could not install the package "+term_colors.HEADER+self.name+term_colors.ENDC)
            return Package.ERR_INSTALL_FAILED

        f = open(self.path/"info.json","w+")
        f.write("{}")
        f.close()
        print(TCIA+term_colors.GREEN+"Successfully installed "+term_colors.HEADER+self.name+term_colors.ENDC)
        return 0


class PackageManager:
    def __init__(self):
        cia_package = os.path.expanduser("~/ciavelli_packages")
        lsdir = os.listdir(cia_package)
        self.packages = []
        self.healthy_packages = 0
        for filename in lsdir:
            if os.path.isdir(Path(cia_package)/filename):
                self.packages.append(Package(filename))
                if self.packages[-1].is_installed():
                    self.healthy_packages+=1
    
    def list(self):
        print(TCIA+"Installed packages: "+term_colors.GREEN+str(self.healthy_packages)+term_colors.ENDC+" number of broken packages (builds not running): "+term_colors.FAIL+str(len(self.packages)-self.healthy_packages))
        for pck in self.packages:
            if pck.is_installed():
                print(TCIA+"Found package: "+term_colors.GREEN+pck.getName()+term_colors.ENDC+" at "+term_colors.BLUE+os.path.expanduser("~/ciavelli_packages/"+pck.getName())+term_colors.ENDC)
            else:
                print(TCIA+"Found broken package: "+term_colors.FAIL+pck.getName()+term_colors.ENDC+" at "+term_colors.BLUE+os.path.expanduser("~/ciavelli_packages/"+pck.getName())+term_colors.ENDC)

    


def list_err(args,tresh,text):
    if len(args) < tresh:
        print(text)
        exit(-1)

def execute_command(cmd):
    print(TCIA+cmd)
    return os.system(cmd)


def exit(code):
    sys.exit(code)

    



def create_cmake_prefix_path():
    cia_package_xpp = os.path.expanduser("~/ciavelli_packages")
    lsdir = os.listdir(cia_package_xpp)
    for filename in lsdir:
        if os.path.isdir(cia_package_xpp+"/"+filename):
            if Package.cmake_path != '':
                Package.cmake_path+=";"
            Package.cmake_path += cia_package_xpp+"/"+filename+"/install";

def link_root_to_user():
    cia_package_xpp = os.path.expanduser("~/ciavelli_packages")
    if not os.path.exists(cia_package_xpp):
        print(TCIA,term_colors.HEADER+"Could not found installation trying to link against root"+term_colors.ENDC)
        os.symlink("/ciavelli_packages",os.path.expanduser("~/ciavelli_packages"))
        if not os.path.exists(cia_package_xpp+"/ciavelli.cmake"):
            print(TCIA,term_colors.FAIL+"Could not link against root the installation is corrupted!"+term_colors.ENDC)
            exit(-1)
        else:
            print(TCIA,term_colors.HEADER+"Link against root successful system wide installation finished"+term_colors.ENDC)


def main():
    if platform.system() == 'Windows':
        Package.git_exe = 'git.exe'
        Package.cmake_exe = 'cmake.exe'
        colorama.init()   

    if len(sys.argv) == 1:
        sys.argv.append("-h")
    link_root_to_user()
    print(TCIA+"CIAVELLI Package manager v0.9\n"+TCIA+"This is an alpha version please report errors to "+term_colors.BLUE+"https://github.com/ShadowItaly/Ciavelli\n"+term_colors.ENDC)
 
    create_cmake_prefix_path()

    parser = argparse.ArgumentParser()
    parser.add_argument('--branch','-b', help="Specifies the branch which should be downloaded and installed", default='')
    parser.add_argument('--install','-i',help="Installs the specified repository",default='')
    parser.add_argument('--commit','-c', help="Specifies the commit which will be checked out and installed", default='')
    parser.add_argument('--update','-u', help="Updates the specified package to the newest version and rebuilds it",default='')
    parser.add_argument('--list','-l',help="Lists all installed packages",default='',action="store_true")
    parser.add_argument('--remove','-r',help="Removes the specified packages",default='')
    parser.add_argument('--name','-n',help="Specifies under which name the package should be installed",default='')
    args = parser.parse_args()

    if args.install != '':
        name = ''
        if args.name != '':
            name = args.name
        else:
            name = args.install.split("/")[-1].split(".")[0]
            if args.branch!='' and args.commit != '':
                print(TCIA+term_colors.FAIL+"A commit is unique it does not make sense to define a branch and a commit, either specify branch or commit")
                return -1
            elif args.branch!='':
                name+="@"+args.branch
            elif args.commit !="":
                name+="@"+args.commit
        name = name.lower()

        
        pack = Package(name)
        with pack.get_lockfile():
            try:
                if pack.is_installed():
                    print(TCIA+term_colors.GREEN+"The package "+term_colors.HEADER+pack.getName()+term_colors.GREEN+" is already installed skipping installation"+term_colors.ENDC)
                    return 0
                if not pack.is_downloaded():
                    pack.download_using_git(args.install,args.commit,args.branch)
                pack.build()
                pack.install()
            except PackageError as pck:
                pck.print_error()
                return -1 

    elif args.update != '':
        pack = Package(args.update.lower())
        with pack.get_lockfile():
            try:
                if pack.is_downloaded():
                    pack.update()
                    pack.build()
                    pack.install()
                    return 0
                else:
                    raise PackageError(TCIA+term_colors.FAIL+"Cannot update package "+term_colors.HEADER+args.update+term_colors.FAIL+". Package does not exist..."+term_colors.ENDC)
            except PackageError as pck:
                pck.print_error()
                return -1
    elif args.remove != '':
        pack = Package(args.remove)
        with pack.get_lockfile():
            if not pack.is_downloaded():
                print(TCIA+term_colors.FAIL+"There is no installed package named "+term_colors.HEADER+args.remove+term_colors.FAIL+". Skipping remove."+term_colors.ENDC)
                return -1
            pack.remove_project()
            print(TCIA+term_colors.GREEN+"Removed package "+term_colors.HEADER+args.remove+term_colors.GREEN+" successfully"+term_colors.ENDC)
        return 0
    elif args.list == True:
        apt = PackageManager()
        apt.list()

    return 0
if __name__ == "__main__":
    
    # execute only if run as a script
    main()
