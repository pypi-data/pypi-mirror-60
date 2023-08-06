
<p align="center">
    <a href="https://github.com/ospinakamilo/caos" target="_blank">
        <img src="https://github.com/ospinakamilo/caos/blob/master/src/docs/img/caos_logo.svg" height="100px">
    </a>
    <h1 align="center">CAOS</h1>
    <br>
    <p align="center">Simple Dependency Management for <b>Python 3</b> Projects using <b>pip</b> and <b>virtualenv</b>.</p>
</p>

Usage
------------
Once installed you can use "caos" trough the command line

#### Arguments
 - **--help, -h** - Get documentation about the arguments and usage
 - **--version, -v** - Show the installed version
 - **init** - Create the .json template file for the project
 - **prepare** - Create a new virtual environment
 - **update** - Download the project dependencies
 - **check** - Validate the downloaded dependencies
 - **test** - Run all the unit tests using the unittest framework
 - **unittest** - Run all the unit tests on a given path using the unittest framework
 - **run** - Execute the main entry point script for the project 
 - **python** -  Provide an entry point for the virtual environment's python
 - **pip** -  Provide quick access for the virtual environment's pip module
 
#### Examples
**caos.json** content example
```json
{
  "require":{
    "numpy": "latest",
    "flask": "1.1.1"
  },
  
  "tests" : "./tests",
  "main": "./src/main.py" 
}
```

```console
~$ caos --help     #Get a similar set of instructions to the ones shown here
```
```console
~$ caos --version  #Display the current installed version
```
```console
~$ caos init     #Create the caos.json file in the current directory
```  
```console
~$ caos prepare  #Set up a new virtual environment
```
```console
~$ caos update   #Download the project dependencies into the virtual environment
```
```console
~$ caos check    #Validate the dependencies have been downloaded
``` 
```console
~$ caos test     #Execute all the unit tests available using the unnittest framework if the path is specified in the caos.json file
```
```console
~$ caos unittest ./path/with/unittests  #Execute all the unit tests available in the given path
```
```console
~$ caos run      #Run the main script of the project
```
```console
~$ caos python ./my_script.py  #Execute an script with the virtual environment python binary
```
```console
~$ caos pip install numpy #Use pip from the virtual environment to install a package
```

Requirements
------------

For this project to work you need to have installed **Python >= 3.5**, **pip** and **virtualenv**.
 

Dependencies 
------------
If you are using Python 3 in **Windows** there are no dependencies for you to install.
If you are using **Linux** make sure to install **pip** and **virtualenv** first.
#### Fedora
~~~
sudo dnf install python3-pip python3-virtualenv
~~~

#### Ubuntu
~~~
sudo apt-get install python3-pip python3-venv
~~~

#### Open Suse
~~~
sudo zypper install python3-pip python3-virtualenv
~~~

Installation
------------
If you already installed **pip** and **virtualenv** use the next command to install **caos**.

### Windows
In a command prompt with administrative rights type:
~~~
pip3 install caos
~~~

### Linux
In a terminal window type:
~~~
sudo pip3 install caos
~~~
