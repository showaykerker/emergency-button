# Deploy SikuliX on Windows

## Prerequisition

### Install JDK
1. From [Oracle](https://www.oracle.com/tw/java/technologies/downloads/#jdk23-windows), JDL Windows x64-installer.
2. Double click to install.

### Install Jython Standalone
1. Get Jython Installer from [Jython Official Page](https://www.jython.org/download.html).
2. Double to install.

### Install Maven for Project Management
1. Get installer from [Maven Official Page](https://maven.apache.org/download.cgi).
2. Unzip and move to `C:\Program Files\`

### Congifure Environment Variable

- add `JAVA_HOME`. e.g. `C:\Program Files\Java\jdk-23`
- add `MAVEN_HOME`. e.g. `C:\Program Files\apache-maven-3.9.9`
- add `%JAVA_HOME%\bin` and `%MAVEN_HOME%\bin` to `PATH`

**NOTE**: [How to Add Environment Variable on Windows](https://tw.windows-office.net/?p=13178#gsc.tab=0)

