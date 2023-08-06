# sddk

This is a simple Python package to write files to- and read files from [sciencedata.dk](https://sciencedata.dk/). It is especially designed for working with shared folders. It relies mainly upon Python requests library.

sciencedata.dk is a project managed by [DEiC](https://www.deic.dk) (Danish e-infrastrcture cooperation) aimed to offer a robust data storage, data management and data publication solution for researchers in Denmark and abroad (see [docs](https://sciencedata.dk/sites/user/) and [dev](https://sciencedata.dk/sites/developer/) for more info). The storage is accessible either through (1)  the web interface, (2) WebDAV clients or (3) an API relaying on HTTP Protocol (see [docs](https://sciencedata.dk/sites/user/) and [dev](https://sciencedata.dk/sites/developer/) for more info). One of the strength of sciencedata.dk is that it currently supports institutional login from 2976 research and educational institutions around the globe (using [WAYF](https://www.wayf.dk/en/about)). That makes it a perfect tool for international research collaboration. 

The main functionality of the package is in uploading any Python object (dict, list, dataframe) as a text or json file to a preselected shared folder and getting it back into a Python environemnt as the original Python object. It uses sciencedata.dk API in combination with Python requests library.

### Dependencies

* requests
* pandas
* matplotlib
* getpass

### Install and import

To install and import the package within your Python environment (i.e. a jupyter notebook) run:

```
!pip install sddk ### to be updated, use flag --ignore-installed
from sddk import * ### import all functions
```

###  Session configuration

To run the main configuration function below, you have to know the following:
* your sciencedata.dk username (e.g. "123456@au.dk" or "kase@zcu.cz"),
* your sciencedata.dk password (has to be previously configured in the sciencedata.dk web interface),

In the case you want to access a shared folder, you further need:

* **name** of the shared folder you want to access (e.g. "our_shared_folder"),

* **username** of the owner of the folder (if it is not yours)

(Do not worry, you will be asked to input these values interactively while running the function)

To configure a personal session, run:
```python
conf = configure_session_and_url()
```


### Configuration of a session with shared folder

To configure a session pointing to a shared folder, run:

```python
conf = configure_session_and_url("our_shared_folder", "owner_username@au.dk")
```
Running this function, you configura a tuple varible `conf`, containing two objects:
* `s`: a request session authorized by your username and password
* `sddk_url`: default url address (endpoint) for your requests

`conf` is later on used as an input for `write_file()` and `read_file()`.

### write_file()

The most important components of the package are two continuously developed functions: `write_file(path_and_filename, python_object, conf)` and `read_file(path_and_filename, type_of_object, conf)`. 

So far these functions can be used with several different types of Python objects: `str`, `list`, `dictionary`, pandas' `dataframe` and matplotlib's `figure`. These can be written either as `.txt`, `.json` or `.png` files, based simply upon the filename's ending chosen by the user. Here are simple instances of these python objects to play with:

```python
### Python "str" object
string_object =  "string content"
### Python "list" object
list_object = ['a', 'b', 'c', 'd']
### Python "dictionary" object
dict_object = {"a" : 1, "b" : 2, "c":3 }
### Pandas dataframe object
import pandas as pd
dataframe_object = pd.DataFrame([("a1", "b1", "c1"), ("a2", "b2", "c2")], columns=["a", "b", "c"]) 
### Matplotlib figure object
import matplotlib.pyplot as plt
figure_object = plt.figure() # generate object
plt.plot(range(10)) # fill it by plotted values
```

The simplest example is once we want to write a string object into a textfile located at our home folder (Remember, that since the configuration this home folder is contained within the `sddk_url` variable ) 

```python
write_file("test_string.txt", string_object, conf)
```

In the case  that everything is fine, you will receive following message:

```
> Your <class 'str'> object has been succefully written as "https://sciencedata.dk/files/test_string.txt"
```

However, there is a couple of things which might go wrong. You can choose an unsupported python object, a non-existent path or unsupported file format. The function captures some of these cases. For instance, once you run `write_file("nonexistent_folder/filename.wtf", string_object, conf)`, you will be interactively asked for corrections. First: the function checks whether the path is correct. When corrected to an existent folder (here it is "personal_folder"), the function further inspect whether it has known ending (i.e. `txt`, `json` or `png`). If not, it asks you interactively for correction. Third, it checks whether the folder already contain a file of the same name (to avoid unintended overwritting), and if yes, asks you what to do. Finally, it prints out where you can find your file and what type of object it encapsulates. 

```
>>> The path is not valid. Try different path and filename: personal_folder/textfile.wtf
>>> Unsupported file format. Type either "txt", "json", or "png": txt
>>> A file with the same name ("textfile.txt") already exists in this location.
Press Enter to overwrite it or choose different path and filename: personal_folder/textfile2.txt
>>> Your <class 'str'> object has been succefully written as "https://sciencedata.dk/files/personal_folder/textfile2.txt"
```

The same function works with dictionaries, lists, Matplotlib's figures and especially Pandas' dataframes. Pandas' dataframe is my favorite. I send there and back 1GB+ dataframes as json files on a daily basis. 

### read_file()

On the other side, we have the function `read_file(path_and_filename, object_type)`, which enables us to to read our files back to python as chosen python objects. Currently, the function can read only textfiles as strings, and json files as either dictionary, lists or Pandas's dataframes. You have to specify the type of object as the second argument, the values are either "str", "list", "dict" or "df" within quotation marks, like in these examples:

```python
string_object = read_file("test_string.txt", "str", conf)
string_object
>>> 'string content'
```

```python
list_object = read_file("simple_list.json", "list", conf)
list_object
>>> ['a', 'b', 'c', 'd']
```

```python
dict_object = read_file("simple_dict.json", "list", conf)
dict_object
>>> {'a': 1, 'b': 2, 'c': 3}
```

```python
dataframe_object = read_file("simple_df.json", "df", conf)
>>>     a   b   c
0  a1  b1  c1
1  a2  b2  c2
```



### PUT and GET requests in detail

In the core of  the`write_file()`function is the PUT request command. Here is  what it basically does in the case of different types of objects:

##### String to TXT

Upload (export) simple text file:

```python
s = conf[0]
sddk_url = conf[1]
s.put(sddk_url + "testfile.txt", data="textfile content")
```

Get it back (import) to Python:

```python
string_testfile = ast.literal_eval(s.get(sddk_url + "testfile.txt").text)
print(string_testfile)
```

##### Pandas DataFrame to JSON

Upload a dataframe as a json file:

```python
import pandas as pd
df = pd.DataFrame([("a1", "b1", "c1"), ("a2", "b2", "c2")], columns=["a", "b", "c"]) 
s.put(sddk_url + "df.json", data=df.to_json())
```

Get it back:

```python
df = pd.DataFrame(s.get(sddk_url + "df.json").json())
```

##### Pandas DataFrame to CSV

```python
import pandas as pd
df = pd.DataFrame([("a1", "b1", "c1"), ("a2", "b2", "c2")], columns=["a", "b", "c"]) 
df.to_csv("df.csv") ### temporal file
s.put(sddk_url + "df.csv", data = open("df.csv", 'rb'))
```

##### Dictionary to JSON

To sciencedata.dk:

```python
dict_object = {"a" : 1, "b" : 2, "c":3 }
s.put(sddk_url + "dict_file.json", data=json.dumps(dict_object))
```

From sciencedata.dk:

```python
dict_object = json.loads(s.get(sddk_url + "dict_file.json").content)
```

##### Matplotlib figure to PNG

```python
import matplotlib.pyplot as plt
fig = plt.figure()
plt.plot(range(10))
fig.savefig('temp.png', dpi=fig.dpi) ### works even in Google colab
s.put(sddk_url + "temp.png", data = open("temp.png", 'rb'))
```

### Next steps
- to make the functions more robust.

The package is built following [this](https://packaging.python.org/tutorials/packaging-projects/) tutorial.

### Credit

The package is continuously develepod and maintained by [Vojtěch Kaše](http://vojtechkase.cz) as a part of the digital collaborative research workflow of the [SDAM project](https://sdam-au.github.io/sdam-au/) at Aarhus University, Denmark. To cite this package, use:

### Version history

* 1.3 - `conf` corrected
* 1.2 - `conf` variable added
* 1.1 - a simple correction
* 1.0 -  functions `write_file()` and `read_file()` added
* 0.1.2 -  redirection added
* 0.1.1 - added shared folder owner argument to the main configuration function; migration from test.pypi to real pypi
* 0.0.8 - shared folders reading&writing for ordinary users finally functional
* 0.0.7 - configuration of individual session by default
* 0.0.6 - first functional configuration



