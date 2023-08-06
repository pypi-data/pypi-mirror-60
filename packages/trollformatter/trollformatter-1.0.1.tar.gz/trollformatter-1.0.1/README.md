# Trollformatter: Troll your fellow devs and compsci teachers

Ever wanted to troll someone by formatting your C/C++/Java code like this?

![ew.jpg](https://external-preview.redd.it/P1B98VFlL6po1QqQRepzJc0O7npbCjUAZTGPh4Leh3A.png?auto=webp&s=de0b625451dca744131e9ede0af65ec858e8580b)

Well now you can.

## What is this? ##
Trollformatter is a formatter inspired by the image above. It basically moves all your semicolons,
braces, etc. to the edge of the file to make it appear to not have semicolons or braces. The
generated code looks much cleaner (/s), and still runs the same as the original file.

DISCLAIMER: DO NOT USE THIS IN ANY KIND OF PRODUCTION ENVIRONMENT. THE TROLLFORMATTER PROGRAM
IS IN ALPHA AND IS NOT GUARANTEED TO WORK PROPERLY AT ALL TIMES. THE DEVELOPERS OF THIS
PROGRAM ARE **NOT** RESPONSIBLE IF YOU LOSE YOUR JOB OR GET A FAILING GRADE BECAUSE
YOU USED THIS.

## How do I run Trollformatter? ##

1. Get Python.
2. Run `python3 setup.py install`. (you may need `sudo` or `--user`).
3. Get your code.
4. Run `trollformatter file.java` (or `.c` or `.cpp`)
5. Check the `file_troll.java` file. If you are satisfied
with the result, you may remove the original and rename this
one.
6. Watch your compsci teacher explode.

## Sounds interesting. How can I contribute? ##

If you want to help out the trollformatter project,
check out the issues board on Gitlab (or test the program
and log undiscovered issues). You can assign an
issue to yourself, fork the project, and send
in a merge request when you're ready to merge your
code.
