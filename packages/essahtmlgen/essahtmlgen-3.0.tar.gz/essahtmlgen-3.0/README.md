#### essahtmlgen

Python tool for creating HTML specific layouts with source code files.
Uses CSU images as the default.
The source code is formatted with a javasript library to be 'pretty'

Here are some examples (Im on OSX):

- Create a 6 part assignment (very basic no source)


essahtmlgen --dest ~/Desktop --name bayleaf --id 2631542 --parts 3 --assignment 1



- Create a the 3 part assignment 1 and embed Random/ClosestPoint.java twice in part 1 and once in part3.


essahtmlgen --dest ~/Desktop --name bayleaf --id 2631542 --parts 3 --assignment 1 --embed 1:Random/ClosestPoint.java,Random/ClosestPoint.java 3:Random/ClosestPoint.java