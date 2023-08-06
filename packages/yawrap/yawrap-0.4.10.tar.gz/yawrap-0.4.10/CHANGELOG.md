#Changelog starts at v0.4 (July 2018)
## 0.4 - brand new tag engine
* Yawrap gets own XML engine
* Yawrap's repository is moved to gitlab & travis

### 0.4.5
* adopting to `pytest v4` and tighter `flake8` restrictions

### 0.4.6
* fixing creation of new `html` files in `cwd`/`pwd` directory
* starting this `CHANGELOG`

### 0.4.7
* minor improvements for navigated yawrap

### 0.4.8
* bugfix of rendering text out of non-string objects

### 0.4.9
* adding tests for python3.8
* discontinued python3.4 compatibility (tests not performed, but may still work)
* improving minor functionality
  - no css nor js file overwriting if already exists 
    (it's up to user to clean target before render)
* adding 40+ SVG attributes substitutions (to be used as keyword-arguments)

### 0.4.10
* fix warning that claims that file exists
