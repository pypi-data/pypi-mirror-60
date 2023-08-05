# Terraform Installer [terraform-installer, ti]  
  
command line installer for the open source version of [terraform](https://www.terraform.io/)  

`ti` is still in the early stages of development. it has been tested in the following platforms:
```
Ubuntu Linux ARM
Ubuntu Linux amd64
Darwin and64
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
  
# install a specific release of given platform  
ti darwin_amd64 -r 0.12.1  
```   

