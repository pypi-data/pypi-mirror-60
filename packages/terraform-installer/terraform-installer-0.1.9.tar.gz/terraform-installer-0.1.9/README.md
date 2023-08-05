# Terraform Installer [terraform-installer, ti]  
  
command line installer for the open source version of [terraform](https://www.terraform.io/)  

`ti` is still in the early stages of development. it has been tested in the following platforms:
```
Linux-4.15.0-1057-aws-x86_64-with-debian-buster-sid  
Darwin-18.7.0-x86_64-i386-64bit   
```   
  
## Installation  
  
```
pip install terraform-installer  
```  
  
### Usage  
  
```
# show help and exit  
ti -h  
  
# install or upgrade, attempt to figure out the platform  
# this is still experimental on most platforms  
ti  
  
# install or upgrade specific platform  
ti darwin_amd64  
  
# install a specific version of given platform  
ti darwin_amd64 -r 0.12.1  
```   

