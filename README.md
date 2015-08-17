autoexam
========

A simple exam generator and grader written in Python with OpenCV


Installing in Linux
===================

```bash
sudo apt-get install texlive texlive-lang-spanish python-opencv python-jinja2 python-qrcode python-zbar python-alsaaudio python-flask
```

How it works
============

Create an exam by following the example format shown in the file example-master.txt.

Afterwards, run the following command:

```bash
python generador.py [master-exam-file.txt]
```

If you do not specify a filename, it will look by default for a file named 'master.txt' in the current folder.

This will generate the exams under a 'generated' folder. To avoid overwriting old generated exams, there will be a 'v#' folder for each generated exam.

The following files will be automatically generated:

* Master.tex: [TODO: ???]
* Test-x.tex: Templates for the exams questions text.
* Answer-x.tex: These contain the templates for generating the answer sheets for each generated exam.
* qrcode-x.png: A qrcode for each exam containing [TODO: ???].
* Solution.txt: A plain text file containing [TODO: ???]
* Order.txt: A JSON file containing [TODO: ???]

[TODO: Where to specify the number of exams to generate?]
[TODO: Where to specify student names?]

You can directly generate the corresponding pdfs by using the provided 'generateLatex' script, passing as an argument the id of the exam you want to generate (for example, v1 if it is the first exam you've generated). (Note: you need to have a valid pdflatex interpreter installed in your system!)

```bash
./generateLatex v{x}
```

This script will also reorganize the generated files into 'pdf' and 'src' folders.

The next step would be actually printing out the exams and torturing the students a little. :)

After you've got your answer sheets filled up, run the following command:




