# AUR_UPD

*Yet another AUR helper with a silent install/update capability*

Author: **Vladimir Kamensky**

Release date: **2020-01-23**

### v 1.1.0 

***
## INSTALL
From pip:

	pip3 install aur_upd
	
Manually:

	python setup.py install
	
## USAGE

Update all AUR packages

	aur_update

Install package from AUR

	aur_update install *package_name*
	
For *install* option or running without any option you can use **--build-log** flag for showing the cause of error if build process was unsuccess

	aur_update install *package_name* --build-log

**--list** option could be used for print all AUR installed packages

	aur_update --list