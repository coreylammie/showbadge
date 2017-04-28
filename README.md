[![license](https://img.shields.io/github/license/hangpark/showbadge.svg)](LICENSE) [![python v3.4, v3.5, v3.6](https://img.shields.io/badge/python-v3.4,_v3.5,_v3.6-blue.svg)](https://www.python.org/)

# ShowBadge

**[ Dynamic badge generator ]**
Gives a fancy badge with custom key-value for the specific branch of user's repository.

## Introduction

Many GitHub repositories are using badges to inform configures, statuses, or other features of it, usually at the top of README. Some of these badges are dynamically made from continuous integration services, such as [Travis-CI](https://travis-ci.org/).

But those CI services are not providing badges enoughly to let users set a value from the results from them appropriately. For example, *Travis-CI* only supports badges **whether build is success or not**, but some users may want to get other (non-discrete) results like *number of tests success*, *times to build*, or *size of build results*. These values can be calculated easily in CI services, but cannot be passed to the GitHub repository in the form of badge.

This service makes you can deal with results from CI services in your repository with custom badge.

## Work Flow

When user pushes a commit:

1. User pushes a commit to the repository
2. CI service is automatically triggered and starts to build
3. CI service sends some result to ShowBadge server with data below:
    - username
    - repository name
    - commit SHA
    - key for data
    - result data
4. ShowBadge server stores data in its db

When user reads README file:

1. README file includes ShowBadge url like:
    - `https://~~~~~~.com/<user>/<repo>/?branch=<branch>&key=<key>`
2. User accesses README file to read
3. ShowBadge server recieves `<user>`, `<repo>`, `<branch>`, and `<key>`
4. ShowBadge server finds corresponding data
5. ShowBadge returns a ShieldsIO url of badge with custom data to README page
6. README page shows our target badge

## Notes

- This project **does not have an actual server**. You should build your own server with Django source codes of this project and run it.
- This project **does not deal with authentication** *yet*. So basically anyone can register data for your repository if he/she knows your server url. (Will be updated in future release.)


## Build Server

1. Clone this repository on your target server.
2. Configure `showbadge/settings.py` and (or not) `showbadge/uwgi.py` to connect Django project to your DB and (or not) web server. (Or you can add `showbadge` as an app to your existing Django project.)
3. Run server.

Make sure to use **Python ≥3.4**.

### Testing

If you are not familiar to Django or if you just want to test, follow:

```bash
$ git clone https://github.com/hangpark/showbadge.git
$ cd showbadge
$ pip install -r requirements.txt
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py runserver
```

Then you can access to the server by `http://127.0.0.1:8000/`. To test it, send POST request to the test server as below (make sure copy the latest commit SHA with full 40 digits of a branch of your public repository):

```bash
$ curl -X POST -d "commit={40-digits-sha}&key=test&value=40%" http://127.0.0.1:8000/{user}/{repo}/
```

And then enter `http://127.0.0.1:8000/{user}/{repo}/?branch={branch}&key=test` via a browser. Then you can see a yellow badge. Test many times you want by changing `value` or adding `&color={color}`.

## Configure CI

You can add manually below shell script into your CI build script to send data to your ShowBadge server:

```bash
$ curl -X POST -d "commit={40-digits-sha}&key={key}&value={value}" http://{your-server}/{user}/{repo}/
```

Initially, GitHub serves a badge image in README by caching via `CAMO` in 1 day. To force update the image, you can use

```bash
$ curl -X PURGE https://camo.githubusercontent.com/{your-img-id}
```

**OR** use built-in script for some CI services listed in below.

### Travis-CI

If you're using [Travis-CI](https://travis-ci.org/) for your project, you don't need to deal with Git or GitHub things manually. `.showbadge-travis.sh` is going to do it for you *(except for pull-request builds)*.

1. Copy `.showbadge-travis.sh` to your project's repository.
2. Add an environment `SHOWBADGE_SERVER` to `settings` of the repository in `Travis-CI` with your server URL.
3. Add an environment `SHOWBADGE_CAMO` to your `settings` of the repository in `Travis-CI` with your GitHub image URL. *(optional)*
4. Add `./.showbadge-travis.sh <key> <value>` to your `.travis.yml` file with your custom key-value. *(`after_success` is recommended)*

If you want to save more than one data with different keys, just repeat step 4.

**Example**
If `grade` file containing the grade of format `Total: XX.X%/100.0%` together with specific details would be created after the build success, we can make `.travis.yml` to send key-value as `grade` and `XX.X/100.0`, respectively:

```yml
language: bash

env:
  - SHOWBADGE_SERVER=http://your.showbadge.server.com/

script:
  - build-your-project

after_success:
  - ./.showbadge-travis.sh grade `sed -n 's/^Total:\ \([0-9.]\+\)%\/\([0-9.]\+\)%$/\1\/\2/p' grade`
```

## Usage

Badge image can be obtained from `/<user>/<repo>/?branch=<branch>&key=<key>&color=<color>`. `color` is optional. If color is not given, this would be converted to `auto` by default. If color is invalid, this would be converted to `red` by default.

If a record for the `user-repo-branch-key` has not be arrived yet, maybe due to on CI or something else, color would be `lightgrey` and value would be `undefined`.

If the value is set to `undefined`, then color would be `lightgrey`.

Insert below code to your `README.md` to show your badge:

```markdown
[![YOUR-KEY](http://YOUR.SERVER.URL/USER/REPO/?branch=BRANCH&key=KEY&color=COLOR)](REDIRECT-URL)
```

### Color Formats

Follow one of below forms:

- 6-digits hex code (`ff69b4`, `FFEE72`, etc.)
- built-in color name (`brightgreen`, `green`, `yellowgreen`, `yellow`, `orange`, `red`, `lightgrey`, or `blue`)
- `auto`, `auto-<num>`, or `auto-<num>-<num>` (`auto-120`, `auto-4.3`, `auto--.5-.5`, etc.)

`auto` options render color by the number in fetched value. `auto` is same as `auto-0-100` and `auto-<num>` is same as `auto-0-<num>`. `auto-<num1>-<num2>` sets the range as `<num1>` to `<num2>` and determines color as one of `brightgreen`, `green`, `yellowgreen`, `yello`, `orange`, and `red` by comparing number in `value` to the input range. Note that `brightgreen` is for the maximum of the range and `red` is for the minimum of the range, and rest are mapped in order linearly.

To deal with `auto`, the feched value should follow one of the formats:

- text including a single number (`34%`, `Fail: 0.7`, etc.)
- text including two numbers as `<num1>/<num2>` (`3.2/4.3`, `success 3/10 in total`, etc.)

Second format overlaps the range to 0 to `<num2>`. If the value does not follow above two formats neither but color is set to `auto` formats, then color should be determined as `lightgrey`.
