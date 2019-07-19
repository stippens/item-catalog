# Item Catalog Project

This project encapsulates a broad range of backend web design elements including:

* `vagrant` virtual machine
* `sqlalchemy` python database library
* `flask` server-side framework
* `jinja2` python template engine
* `werkzeug` web server gateway interface
* `oauth2` authentication
* JSON API for database information



The primary purpose of this application is to provide a basic media database for managing book, movie, and video game information.  It demonstrates how to use each of the tools listed above and is primarily a server side application.

## Getting Started

This application uses a virtual machine called [Vagrant](https://www.vagrantup.com/) and uses [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) to install and manage the VM. It is expected that vagrant is installed on the machine running this application.

[This video](https://www.youtube.com/watch?v=djnqoEO2rLc) offers a conceptual overview of virtual machines and Vagrant. You don't need to watch it to proceed, but you may find it informative.

### Bringing up the virtual machine

To begin, open a terminal window in the project directory. The basic commands for bringing the virtual machine online are as follows:

```
vagrant up
vagrant ssh
cd /vagrant
```

The `vagrant up` command starts the virtual machine and the `vagrant ssh` command initiates secure shell access into the vagrant environment.  Finally the `cd /vagrant` command changes the current working directory to the directory shared by the VM and your local machine.

### Starting the Application

In order to start the application simply start the project with:

```
python project.py
```

The application will be served on localhost port 5000 so port your browser to:

```
http://localhost:5000
```

### Shutting down the application

In order to shut down the application, you can type `cntl-C` in the terminal window.  You will also want to shut down the vagrant environment by using the following commands:

```
exit
vagrant halt
```

The `exit` command exits the virtual machine and the `vagrant halt` command shuts down the virtual machine.

## Important File Information

The application is divided into three parts: static content, templates, and python source code.

### Static Content

Static content is stored in the `static` directory.  This directory contains the css files for application appearance and visual behavior.

### Templates

The `jinja2` template environment utilizes the `template` directory for manageing all html templates used in the application. The `main.html` template is the top level template from which all other templates are built.

### Python Source Code

The python source code and media database are stored in the project root directory.  The important files are as follows:

* `project.py` is the application source file
* `database_setup.py` defines the structure of the database
* `create_database.py` adds content to the database for testing
* `mediaCatalog.db` is the database itself
* `client_secret.json` is the google authentication file
