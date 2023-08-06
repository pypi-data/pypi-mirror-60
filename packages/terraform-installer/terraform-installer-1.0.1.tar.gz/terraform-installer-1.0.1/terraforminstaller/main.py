#!/usr/bin/env python

"""install or update to the latest version of terraform open source version"""

import argparse
from argparse import RawTextHelpFormatter as rawtxt
import sys
import signal
import os
import subprocess
import string
import random
import datetime
from os.path import expanduser
import time
import platform as p
from functools import reduce
from zipfile import ZipFile, ZipInfo
from shutil import which, rmtree
import getpass
import re
# outside of the standard lib
import pkg_resources
from stringcolor import cs, bold, underline
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

def signal_handler(sig, frame):
    """handle control c"""
    print('\nuser cancelled')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def query_yes_no(question, default="yes"):
    '''confirm or decline'''
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)
    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("\nPlease respond with 'yes' or 'no' (or 'y' or 'n').\n")

def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""
    return which(name) is not None

def get_versions(first=None):
    """get versions of terraform from the website"""
    website = "https://releases.hashicorp.com/terraform/"
    try:
        response = requests.get(website).text
    except Exception:
        print(cs("SORRY", "red", "lightgrey6")+cs(" cannot get terraform releases.", "yellow"))
        print(cs("please check your internet connection and try again.", "lightgoldenrod"))
        exit()
    soup = BeautifulSoup(response, 'html.parser')
    versions = []
    for list_item in soup.find_all('li'):
        if list_item.contents[1].contents[0] != "../":
            versions.append(list_item.contents[1].contents[0])
    if first is None:
        return versions
    else:
        return versions[0].replace("terraform_", "")

def get_platforms(version):
    """get platforms for version"""
    website = f"https://releases.hashicorp.com/terraform/{version}/"
    try:
        response = requests.get(website).text
    except Exception:
        print(cs("SORRY", "red", "lightgrey6")+cs(" cannot get terraform releases.", "yellow"))
        print(cs("please check your internet connection and try again.", "lightgoldenrod"))
        exit()
    soup = BeautifulSoup(response, 'html.parser')
    platforms = []
    for list_item in soup.find_all('li'):
        if list_item.contents[1].contents[0] != "../" and list_item.contents[1].contents[0] != f'terraform_{version}_SHA256SUMS' and list_item.contents[1].contents[0] != f'terraform_{version}_SHA256SUMS.sig':
            platforms.append(list_item.contents[1].contents[0].replace(f"terraform_{version}_", "").replace(".zip", ""))
    return platforms

def platform_sniffer(machine, system, release):
    """find the closest matching platform"""
    # python machine name to terraform machine name mapping
    pm2tfm = { 
        "i386":"386",
        "x86_64":"amd64",
        "aarch64":"arm",
        "AMD64":"amd64"
    }
    tf_machine = False
    for k, v in pm2tfm.items():
        if k == machine:
            tf_machine = v
    if not tf_machine:
        return False
    system = system.lower()
    contenders = []
    for plat in get_platforms(release):
        if plat.split("_")[0] == system:
            contenders.append(plat)
    if not contenders:
        return False
    if len(contenders) == 1:
        return contenders[0]
    else:
        for cunt in contenders:
            if cunt.split("_")[1] == tf_machine:
                return cunt
    return False

class ZipFileWithPermissions(ZipFile):
    """ Custom ZipFile class handling file permissions. """
    def _extract_member(self, member, targetpath, pwd):
        if not isinstance(member, ZipInfo):
            member = self.getinfo(member)

        targetpath = super()._extract_member(member, targetpath, pwd)

        attr = member.external_attr >> 16
        if attr != 0:
            os.chmod(targetpath, attr)
        return targetpath

def find_best_path_for_exe(best_guess):
    """find best path to store executable file"""
    path = os.environ["PATH"]
    if os.name == "posix":
        path = path.split(":")
    else:
        path = path.split(";")
    if best_guess in path:
        return best_guess
    elif os.path.join(os.path.sep, "usr", "local", "bin") in path:
        return os.path.join(os.path.sep, "usr", "local", "bin")
    elif os.path.join(os.path.sep, "usr", "bin") in path:
        return os.path.join(os.path.sep, "usr", "bin")
    elif os.path.join("C:", "Program Files") in path:
        return os.path.join("C:", "Program Files")
    elif os.path.join("C:", "opt", "hashicorp") in path:
        return os.path.join("C:", "opt", "hashicorp")
    else:
        prefix = best_guess
        while True:
            prefix = input("Directory where you will put terraform executable ["+underline(prefix)+"] : ") or prefix
            if not os.path.isdir(prefix):
                prefix = best_guess
                print(cs("SORRY", "red", "lightgrey6"), cs("directory does not exist", "yellow"))
                continue
            elif prefix not in path:
                print(cs("SORRY", "red", "lightgrey6"), cs(prefix, "SandyBrown"), cs("isn't in your PATH", "yellow"))
                prefix = best_guess
            else:
                break
        return prefix

def find_owner(filename):
    """find owner of dir"""
    if os.name == "posix":
        from pwd import getpwuid
        return getpwuid(os.stat(filename).st_uid).pw_name
    else:
        import win32api
        import win32con
        import win32security
        sd = win32security.GetFileSecurity(filename, win32security.OWNER_SECURITY_INFORMATION)
        owner_sid = sd.GetSecurityDescriptorOwner()
        name, domain, type = win32security.LookupAccountSid(None, owner_sid)
        if name == "Administrators":
            return "Administrator"
        else:
            return name

def terraform_version():
    """get version of currently installed tf exe"""
    sys_version = subprocess.check_output("terraform version", shell=True).decode("utf-8").strip()
    return re.search(r'v*([\d.]+)', sys_version).group(1) 

def id_generator(size=20, chars=string.ascii_uppercase + string.digits):
    """return random string"""
    random_string = ''.join(random.choice(chars) for _ in range(size)).lower()
    right_now = str(datetime.datetime.now()).replace(" ", "-").replace(":", "-").replace(".", "-")
    return right_now + "-terraform-installer-" + random_string

def main():
    '''install or update to the latest version of terraform'''
    version = pkg_resources.require("terraform-installer")[0].version
    parser = argparse.ArgumentParser(
        description='install or update to the latest version of terraform open source version',
        formatter_class=rawtxt
    )

    #parser.print_help()
    parser.add_argument(
        "platform",
        help="""$ ti linux_amd64\n
options are """+str(get_platforms(get_versions(first=True))),
        nargs='?',
        default='none'
    )
    home = expanduser("~")
    parser.add_argument('-r', '--release', help=f"install a specific release. default={get_versions(first=True)}", default=get_versions(first=True))
    parser.add_argument('-y', '--yes', action='store_true', help='approve all prompts as yes.')
    parser.add_argument('-d', '--destination', help='specify a install destination', default='none')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s '+version)
    args = parser.parse_args()
    platform = args.platform
    release = args.release
    yes = args.yes
    specified_dest = args.destination
    all_versions = get_versions()
    rand_str = id_generator()

    # error check for release existing
    if "terraform_"+release not in all_versions:
        print(cs("SORRY", "red", "lightgrey6")+cs(" can't find the release: ", "yellow")+cs(release, "red"))
        print(cs("available versions:", "grey"))
        print(str([version.replace("terraform_", "") for version in all_versions]))
        exit()

    # check that release version includes platform
    if platform != "none":
        if platform not in get_platforms(release):
            print(cs("SORRY", "red", "lightgrey6")+cs(f" can't find the platform: {cs(platform, 'red')}", "yellow")+cs(f" in version {cs(release, 'red')}", "yellow"))
            print(cs("available platforms:", "grey"))
            print(str(get_platforms(release)))
            exit()

#    print(bytes.decode(b'\xF0\x9F\x9A\xA7', 'utf8')+" work in progress. terraform-installer version: {} ".format(version)+bytes.decode(b'\xF0\x9F\x9A\xA7', 'utf8'))
#
    # check for terraform
    terraform_exists = False
    if not is_tool("terraform"):
        print(cs("this program will install terraform", "gold"))
        use_term = ["install", "installing"]
        tf_install_dir = home
    else:
        terraform_exists = True
        if os.name == "posix":
            tf_install_dir = which("terraform").replace(os.sep+"terraform", "")
        else:
            tf_install_dir = which("terraform").replace(os.sep+"terraform.EXE", "")
        print(tf_install_dir)
        # get terraform version
        tf_version = terraform_version()
        print(cs("terraform found.", "lightgreen"), cs("this program will update terraform to", "gold"), cs(release, "steelblue2"))
        if tf_version == release:
            print(cs("WARNING", "red", "lightgrey6"), cs("the currently installed version is the same as the specified release:", "yellow"), cs(tf_version, "steelblue2"))
            use_term = ["reinstall", "reinstalling"]
        else:
            print(cs("currently installed release:", "lightgrey11"), cs(tf_version, "steelblue2"))
            use_term = ["update to", "updating to"]

    if platform == "none":
        print(cs("no platform provided. attempting to sniff...", "grey"))
        # print(cs("platform found:", "grey"), cs(p.sysplat.platform(), "lightgoldenrod"))

        machine = p.machine()
        system = p.system()
        if platform_sniffer(machine, system, release):
            platform = platform_sniffer(machine, system, release)
        else:
            # could not sniff platform
            print(cs(f"could not find a release for machine: {machine}, system: {system}", "yellow"))
            print(cs(f"the following are the supported platforms for the specified release: {release}:", "lightgrey11"))
            print(get_platforms(release))
            print(cs("if you know the platform you want to install, try:", "lightgrey11"))
            print(cs("ti [PLATFORM]", "sandybrown"), cs("# where [PLATFORM] is one of the platforms in the list above.", "grey"))
            exit()
        print(cs(platform, "sandybrown"), cs("seems like the closest match", "lightgrey3"))

    if yes or query_yes_no(f"{use_term[0]} terraform {release}?", "yes"):
        time.sleep(1)
        if os.name == "posix":
            copy_command = "cp"
            executable = "terraform"
        else:
            copy_command = "copy"
            executable = "terraform.exe"
        if specified_dest != "none":
            best_path = specified_dest
        else:
            best_path = find_best_path_for_exe(tf_install_dir)
        if terraform_exists:
            best_path_owner = find_owner(os.path.join(best_path, executable))
            install_dest = os.path.join(best_path, executable)
        else:
            best_path_owner = find_owner(best_path)
            install_dest = best_path
        current_user = getpass.getuser()
        print(current_user, best_path_owner)
        if best_path_owner != "root" and best_path_owner != current_user:
            print(cs("SORRY", "red", "lightgrey6"), cs("you don't own the install destination, and neither does root.", "yellow"))
            print(cs("please try again with a different user or a different install destination.", "lightgoldenrod"))
            exit()
    
        print(cs(f"temporarily downloading terraform {release} for {platform}", "pink"))
        try:
            os.mkdir(os.path.join(home, rand_str))
        except OSError:
            # could not create temp directory
            print(cs("SORRY", "red", "lightgrey6"), cs(f"creation of the directory {os.path.join(home, rand_str)} failed", "yellow"))
            exit()
        destination = os.path.join(home, rand_str, f"terraform_{release}_{platform}.zip")
        print(cs("download path:", "pink"), bold(destination))
        
        # downloading zip file with progress bar
        tf_zipfile = f"https://releases.hashicorp.com/terraform/{release}/terraform_{release}_{platform}.zip"
        r = requests.get(tf_zipfile, stream=True)
        # Total size in bytes.
        total_size = int(r.headers.get('content-length', 0))
        block_size = 1024 #1 Kibibyte
        t = tqdm(total=total_size, unit='iB', unit_scale=True)
        with open(destination, 'wb') as f:
            for data in r.iter_content(block_size):
                t.update(len(data))
                f.write(data)
        t.close()
        if total_size != 0 and t.n != total_size:
            print(cs("SORRY", "red", "lightgrey6"), cs("something went wrong", "yellow"))
            rmtree(os.path.join(home, rand_str))
            exit()
        
        # unzip
        print(cs("unpacking zip file", "pink"))
        with ZipFileWithPermissions(destination) as zfp:
            zfp.extractall(os.path.join(home, rand_str))
        print(cs("unpacked at:", "pink"), bold(os.path.join(home, rand_str, executable)))
        if best_path_owner == "root":
            print(cs("root owns the install destination", "lightgrey11"), cs(install_dest, "sandybrown"))
            print(cs("will attempt to use sudo...", "lightgrey11"))
            cp_cmd = f"sudo cp {os.path.join(home, rand_str, executable)} {best_path}"
            backup_cmd = f"sudo cp {os.path.join(best_path, executable)} {os.path.join(best_path, 'terraform.it.backup')}"
        else:
            cp_cmd = f"{copy_command} {os.path.join(home, rand_str, executable)} {best_path}"
            backup_cmd = f"{copy_command} {os.path.join(best_path, executable)} {os.path.join(best_path, 'terraform.it.backup')}"
        
        # backup old version
        if terraform_exists:
            print(cs("backing up old version to:", "pink"), bold(os.path.join(best_path, "terraform.it.backup")))
            subprocess.call(backup_cmd, shell=True)
        
        # copy new version
        print(cs("copying new executable to", "pink"), bold(best_path))
        subprocess.call(cp_cmd, shell=True)

        # cleaning up
        print(cs("removing temporary directory", "pink"), bold(os.path.join(home, rand_str)))
        rmtree(os.path.join(home, rand_str))

        # done
        print(cs("terraform", "green"), "is now installed")
        subprocess.call("terraform version", shell=True)
    exit()

if __name__ == "__main__":
    main()
