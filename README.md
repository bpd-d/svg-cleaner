# svg-cleaner
Small CLI tool to clean svg-xml files from environment specific nodes
Script gets all files from given **input** or from **./icons** if input was not provided in command line, parse and saves modified in the **output** or folder **./out**

# Requirements
Python 3 installed

# Usage
Run command
```
 python main.py - i <inputfile> -o <outputfile> -j -s -c
```

For help call
```
python main.py -h
```
Options:
* -i [ --input=] Input folder 
* -o [ --output=] Output folder 
* -j [ --json] Create json file 
* -s [ --js] Create JS file 
* -c [ --clean] Clean output folder before conversion