import sys
import os
import platform
import shutil
import multiprocessing
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
def list_err(args,tresh,text):
    if len(args) < tresh:
        print(text)
        exit(-1)
def execute_command(cmd):
    print(TCIA+cmd)
    return os.system(cmd)

print(TCIA+"CIAVELLI Package manager v0.0\n"+TCIA+"This is an alpha version please report errors to "+term_colors.BLUE+"https://github.com/ShadowItaly/Ciavelli\n"+term_colors.ENDC)

def exit(code):
    sys.exit(code)

list_err(sys.argv,2,TCIA+term_colors.FAIL+"Not enough arguments!\n"+TCIA+term_colors.FAIL+"Usage: \"ciavelli [command] [package/url/optional]\""+term_colors.ENDC+"\n"+TCIA+"[commands]:\n"+TCIA+"    install\n"+TCIA+"    update\n"+TCIA+"    remove\n"+TCIA+"    list")

git_exe = 'git'
cmake_exe = 'cmake'
if platform.system() == 'Windows':
    git_exe = 'git.exe'
    cmake_exe = 'cmake.exe'

if sys.argv[1] == 'install':
    list_err(sys.argv,3,TCIA+term_colors.FAIL+"Not enough arguments!\n"+TCIA+term_colors.FAIL+"Usage: \"ciavelli install [package/url]\""+term_colors.ENDC)
    name = ''
    branch = ''
    commit = ''
    prefix = ''
    for it in sys.argv[2:]:
        if it == '--branch':
            prefix = 'branch'
        elif it == '--commit':
            prefix = 'commit'
        else:
            if prefix == 'branch':
                branch = it
                prefix = ''
                continue
            elif prefix == 'commit':
                prefix = ''
                commit = it
                continue
            elif prefix == '' and name =='':
                name = it.split("/")[-1].split(".")[0]
            else:
                print(TCIA+term_colors.FAIL+"Multiple urls passed, aborting please just specify one url")
                exit(-1)
    if branch!='' and commit != '':
        print(TCIA+term_colors.FAIL+"A commit is unique it does not make sense to define a branch and a commit, either specify branch or commit")
        exit(-1)
    elif branch!='':
        name+="@"+branch
    elif commit !="":
        name+="@"+commit

    branch = branch+commit
    cia_package = os.path.expanduser('~/ciavelli_packages/'+name)
    
    if os.path.isfile(cia_package+"/info.json"):
        print(TCIA+term_colors.GREEN+"Found package "+name+" won't reinstall package. To update use \"ciavelli update "+name+"\""+term_colors.ENDC)
    else:
        print(TCIA+"Creating package directory: "+cia_package)
        os.makedirs(cia_package,exist_ok=True)

        print(TCIA+"Creating build directory at: "+os.path.expanduser('~/ciavelli_packages/'+name+'/ciavelli_build'))
        os.makedirs(os.path.expanduser('~/ciavelli_packages/'+name+'/ciavelli_build'),exist_ok=True)
        print(TCIA+"Creating source directory at: "+os.path.expanduser('~/ciavelli_packages/'+name+'/git_clone'))
        doesdir_exist = not os.path.isdir(cia_package+"/git_clone")
        if doesdir_exist and (execute_command(git_exe+' clone '+sys.argv[2]+' '+os.path.expanduser('~/ciavelli_packages/'+name+'/git_clone')) != 0):
            print(TCIA+term_colors.FAIL+"Could not clone the package from path: "+sys.argv[2])
            shutil.rmtree(cia_package)
            exit(-1)
        if branch != '' and (execute_command("cd "+cia_package+"/git_clone &&"+git_exe+' checkout '+branch)!=0):
            print(TCIA+term_colors.FAIL+"Could not find the specified branch/commit "+branch)
            shutil.rmtree(cia_package)
            exit(-1)

        if execute_command("cd "+os.path.expanduser('~/ciavelli_packages/'+name+'/ciavelli_build')+'&&'+cmake_exe+" ../git_clone -DCMAKE_INSTALL_PREFIX="+cia_package+"/install &&"+cmake_exe+" --build . -j"+str(multiprocessing.cpu_count())+" &&"+cmake_exe+" --install .") != 0:
            print(TCIA+term_colors.FAIL+"Could not install the package "+name+term_colors.ENDC)
            exit(-1)
        
        f = open(cia_package+"/info.json","w+")
        f.write("{}")
        f.close()
        print(TCIA+term_colors.GREEN+"Successfully installed "+name+term_colors.ENDC)
elif sys.argv[1] == 'update':
    list_err(sys.argv,3,TCIA+term_colors.FAIL+"Not enough arguments!\n"+TCIA+term_colors.FAIL+"Usage: \"ciavelli update [package/url]\""+term_colors.ENDC)

    name = sys.argv[2].split("/")[-1].split(".")[0]
    cia_package = os.path.expanduser('~/ciavelli_packages/'+name)
    if os.path.isdir(cia_package):
        if execute_command("cd "+os.path.expanduser('~/ciavelli_packages/'+name+'/git_clone')+"&& git pull") != 0:
            print(TCIA+term_colors.FAIL+"Could not pull changes from upstream: "+sys.argv[2])
            exit(-1)

        print(TCIA+"Installing to temporary directory "+cia_package+"/ciavelli_tmp")
        if execute_command("cd "+os.path.expanduser('~/ciavelli_packages/'+name+'/ciavelli_build')+'&&'+cmake_exe+" ../git_clone -DCMAKE_INSTALL_PREFIX="+cia_package+"/ciavelli_tmp &&"+cmake_exe+" --build . -j"+str(multiprocessing.cpu_count())+" &&"+cmake_exe+" --install .") != 0:
            print(TCIA+term_colors.FAIL+"Could not install the package "+name+term_colors.ENDC)
            exit(-1)
        print(TCIA+term_colors.GREEN+"Installation succesfull, overwriting existing installation now.")
        shutil.rmtree(cia_package+"/install")
        os.rename(cia_package+"/ciavelli_tmp",cia_package+"/install")

        f = open(cia_package+"/info.json","w+")
        f.write("{}")
        f.close()
        print(TCIA+term_colors.GREEN+" Successfully updated "+name+term_colors.ENDC)
    else:
        print(TCIA+term_colors.FAIL+"There is no package "+name+" installed for this user")
elif sys.argv[1] == 'remove':
    list_err(sys.argv,3,TCIA+term_colors.FAIL+"Not enough arguments!\n"+TCIA+term_colors.FAIL+"Usage: \"ciavelli remove [package/url]\""+term_colors.ENDC)
    name = sys.argv[2].split("/")[-1].split(".")[0]
    cia_package = os.path.expanduser('~/ciavelli_packages/'+name)
    if os.path.isdir(cia_package):
        shutil.rmtree(cia_package)
        print(TCIA+term_colors.GREEN+"Successfully removed package "+name)
    else:
        print(TCIA+term_colors.FAIL+"There is no package "+name+" installed for this user")
elif sys.argv[1] == 'list':
    cia_package = os.path.expanduser("~/ciavelli_packages")
    lsdir = os.listdir(cia_package)
    whatever='';
    whatever_broken=''
    numpackages = 0
    numpackages_broken = 0
    for filename in lsdir:
            if filename != 'ciavelli.cmake':
                if os.path.isfile(cia_package+"/"+filename+"/info.json"):
                    whatever+=TCIA+term_colors.GREEN+"Found package: "+filename+" at "+os.path.expanduser("~/ciavelli_packages/"+filename)+term_colors.ENDC+"\n"
                    numpackages+=1
                else:
                    numpackages_broken+=1
                    whatever_broken+=TCIA+term_colors.FAIL+"Found broken package: "+filename+" at "+os.path.expanduser("~/ciavelli_packages/"+filename)+term_colors.ENDC+"\n"
    print(TCIA+"Installed packages: "+term_colors.GREEN+str(numpackages)+term_colors.ENDC+" number of broken packages (builds not running): "+term_colors.FAIL+str(numpackages_broken))
    if whatever != '':
        print(whatever,end = '')
    if whatever_broken != '':
        print(whatever_broken)
else:
    print(TCIA+term_colors.FAIL+"Unknown command \""+sys.argv[1]+"\"\n"+TCIA+term_colors.FAIL+"Usage: \"ciavelli [command] [package/url/optional]\""+term_colors.ENDC+"\n"+TCIA+"[commands]:\n"+TCIA+"    install\n"+TCIA+"    update\n"+TCIA+"    remove\n"+TCIA+"    list")
exit(0)
