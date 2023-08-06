# augmentedtree

![augmentedtree icon](https://gitlab.com/david.scheliga/augmentedtree/raw/dev/docs/resources/augmentedtree-icon.png "Circle, square, triangle and lines.")

`augmentedtree` enhances mappings and sequences (targeted for python
dictionaries and lists) preserving their native behavior and access.
The enhancement comes with getting values by single keys, human readable
viewing, selecting and setting multiple values/items within the nested
data at once, *or*-conditional selection of values/items. Also this package
intends to prepare the nested data for pyQt. The augmentation provides
methods and properties to be used for a `QAbstractItemModel` showing
the nested data within a `QTreeView`.

## Installation

Installing the latest release using pip is recommended.

```` shell script
    $ pip install augmentedtree
````

The latest development state can be obtained from gitlab using pip.

```` shell script
    $ pip install git+https://gitlab.com/david.scheliga/augmentedtree.git@dev
````

## Basic Usage
The major purpose of augmentedtree is to retrieve quickly specific value(s) from a deep
nested data featuring:

- unix filename pattern
- regular expressions
- *or*-conditional selection

The targeted usage is to be able to write the following kind of code

````
# code where the nested data comes from
...

# gathering parameters
with AugmentedTree(nested_data) as tree:
    # simple selection
    first_value = tree.select("something", "here")[0]
    last_value = tree.select("something", "there")[-1]
    a_slice_of_values = tree.select("a", "l?t", "of")[3:6]

    # selection with refinement
    selection_of_values = tree.select("also/a", "lot", "of")
    narrowed_down = selection_of_values.where("this", "or", "that")[ALL_ITEMS]
    ...


if not tree.all_selections_succeeded:
    # break, exit or reacting to some value are not there
    ...

# code which is working with requested parameters       
...
````

[Read-the-docs](https://augmentedtree.readthedocs.io/en/latest/) for a detailed 
explanation on how to use augmented tree.

## Contribution

Any contribution by reporting a bug or desired changes are welcomed. The preferred 
way is to create an issue on the gitlab's project page, to keep track of everything 
regarding this project.

### Contribution of Source Code
#### Code style
This project follows the recommendations of [PEP8](https://www.python.org/dev/peps/pep-0008/).
The project is using [black](https://github.com/psf/black) as the code formatter.

#### Workflow

1. Fork the project on Gitlab.
2. Commit changes to your own branch.
3. Submit a **pull request** from your fork's branch to our branch *'dev'*.

## Authors

* **David Scheliga** 
    [@gitlab](https://gitlab.com/david.scheliga)
    [@Linkedin](https://www.linkedin.com/in/david-scheliga-576984171/)
    - Initial work
    - Maintainer

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE - see the
[LICENSE](LICENSE) file for details

## Acknowledge

- [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
