essahtmlgen

Python tool for creating HTML specific layouts with source code files.
Uses CSU images as the default.
The source code is formatted with a javasript library to be 'pretty'

Here are some examples (Im on OSX):

- Create a 6 part assignment (very basic no source)


essahtmlgen --destination ~/Desktop --name bayleaf --id 2631542 --parts 6 --assignment 1


This will create 'Assignment1' on the desktop with 6 basic parts.


- Create a the 3 part assignment 1  with a source

A source directory contains folders which will become named parts (as well as the .html versions).
The files in each directory will be used to compose the specfic parts html file.
Java code will turn into pretty embedded source code.
Text code will turn into paragraph tags.
There is no order right now so you may have to play around with it after but generally it follows the directory structure.

Create a source directory structured like this:
    test
        | FirstPart
                        | data.txt
                        | JavaCode.java
        | SecondPart
                        | file.txt

essahtmlgen --destination ~/Desktop --name bayleaf --id 2631542 --parts 2 --assignment 1 


This will create 'Assignment1' on the desktop with two parts: FirstPart and SecondPart.