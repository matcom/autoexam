# Autoexam

A simple exam generator and grader written in Python with OpenCV.


## Getting Started

Currently, the only supported platform is Linux. Support for other operating systems is on it's way. ;)

To install dependencies in a Debian based Linux distribution, just run the following command as superuser:

```bash
apt-get install texlive texlive-lang-spanish python-opencv \
python-jinja2 python-qrcode python-zbar python-alsaaudio python-flask
```

You should also install `poppler-utils` as a temporary development dependency.

The recommended way to use Autoexam is installing it globally into your system.
You can use the provided `install.sh` script for this.

```bash
cd /path/to/autoexam
sudo ./install.sh
```

The rest of the examples in this README will assume you did this.

## How it works

You can use Autoexam both as a command line tool, or with a PyQt GUI.

### Command Line Interface

To create a new project, just type:

```bash
autoexam new 'test_name'
cd 'test_name'
```

You can define your questions database by editing the `master.txt` file. Use this file as well
to specify how many questions you'd like in your exams, and how many of each tag.

Afterwards, run the following command:

```bash
autoexam gen -c number_of_exams
```

Your exams will be generated in pdf format in the `/path/to/project/generated/last` folder.

The next step would be actually printing out the exams and torturing the students a little. :)

After you've got your answer sheets filled up, run the following command:

```bash
autoexam scan
```

At this point, you can modify the default grader sheet if needed.
It's just a text file inside the `generated` folder.

The last thing to do is to actually grade the exams. It's pretty simple:

```bash
autoexam grade
```

This will create a `grades.json` file with the results. Pretty simple, right?

GUI
---

Just run:

```
autoexam qtui
```

...and a wizard-like interface will pop up. If it is run from inside a project folder,
it will automatically be loaded. It's all pretty intuitive, so... enjoy! :)

Currently there is no UI for editing the gradersheet. It's just a text file `grader.txt` inside the generated folder, so feel free to edit it. The syntax is similar to this: [points_for_selecting:points_for_unselecting] * number_of_options. This should probably get more user friendly in the near future.

### Contributing

Whether it's code, ideas, suggestions, or whatever, contributions are more than welcome!
Please check the AUTHORS file and contact any of us through email.

Or if you feel adventurous enough, you can always clone/fork the project
and then do a pull request. ;)
