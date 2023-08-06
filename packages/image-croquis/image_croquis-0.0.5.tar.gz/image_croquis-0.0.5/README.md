# image_croquis
An example python package which works as a command line tool as well as importable module with a basic use case

## Installation

```bash
$ pip install image-croquis
```

## Basic Usage

```bash
system@user:$ image_croquis -h

usage: image_croquis [-h] [-i IMG_PATH] [-o OUTPUT_DIR]

optional arguments:
  -h, --help            show this help message and exit
  -i IMG_PATH, --img-path IMG_PATH
                        Specify the image path
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Directory where you want to the output
```

## Command Line

```bash
$ image_croquis --img-path <Specify the location of the image> --output-dir <Directoy name where the output needs to be stored>
```

#### Example

```bash
$ image_croquis --img-path /home/users030/Downloads/input.jpeg --output-dir /tmp/
```

#### Output

|Input|Output|
|-----|------|
|![](images/input.jpeg)|![](images/output.jpeg)|


## Importing

```python
>>>
>>> import image_croquis
>>>
>>>
>>> process = image_croquis.ImageCroquis("/home/users030/Downloads/car.jpeg", "/tmp/")
>>>
>>> process.run()
Output image is saved in the specified path
>>>
>>>
```
