# Tyrian Sphinx Theme

A Sphinx theme based on Tyrian (the new unified gentoo.org theme). 


- [Installation](#installation)
- [Configuration](#configuration)
    - [builders](#builders)
    - [sidebar](#sidebar)
    - [navigationlinks_top](#navigationlinks_top)
    - [navigationlinks_bottom](#navigationlinks_bottom)
    - [navigationlinks_navbar](#navigationlinks_navbar)
    - [license](#license)
    - [license_link](#license_link)
- [Contributors](#contributors)

## Installation
You can install the theme using 
``` shell
$ pip install git+https://github.com/mmagorsc/tyrian_sphinx_theme/#egg=tyrian_sphinx_theme
```

## Configuration
The appereance of the theme can be adjusted using different builders as well as further html_theme_options:

### builders

It is possible to use two different builders: 
- html-builder *(default)*: Creates multiple pages, i.e. one page per file
- singlehtml-builder: Creates a single large page, containing the whole content

You can specify the builder using sphinx command line options like: 
```
$ sphinx-build -b singlehtml ...
```

### sidebar

- right *(default)*: display the sidebar on the right side of the page
- left: display the sidebar on the left side of the page
- none: don't display the sidebar on the page at all

### navigationlinks_top

- short: display the links using "<< >>"
- long: display the links using "<< chapter-heading chapter-heading >>"
- none *(default)*: don't display the navigation links on top at all
    
### navigationlinks_bottom

- short: display the links using "<< >>"
- long *(default)*:  display the links using "<< chapter-heading chapter-heading >>"
- none: don't display the navigation links at the bottom at all
    
### navigationlinks_navbar

- short: display the links using "<< >>"
- long:  display the links using "<< chapter-heading chapter-heading >>"
- none *(default)*: don't display the navigation links in the navbar at all

### license

- the license that will be display in the footer
- CC-BY-SA-4.0 *(default)*

### license_link

- the link to the license that will be used when clicking on the license in the footer
- https://creativecommons.org/licenses/by-sa/4.0/ *(default)*

## Contributors
* [Max Magorsch](mailto:max@magorsch.de)