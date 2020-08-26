---
layout: page
title: "Data Subsetting"
category: doc
date: 2020-03-25 22:44:51
order: 7
use_math: true
---
<!-- AMiGA is covered under the GPL-3 license -->

You can use `AMiGA` to analyze only specific wells even if they are spread across different plates. To do this, you can utilize `AMiGA` subsetting function. Here are a couple examples that will explain how to do this.

<br />

**Example One**

You have 100s of files in your data folder. But you only want to analyze wells corresponding to two specific isolates.

```bash
python amiga.py -i /Users/firasmidani/experiments -s Isolate:CD_treA,CD_treX --merge-summary -o CD_treA_treX
```

The subsetting argument above assumes that the relevant mapping files will have the `Isolate` column. This can be auto-generated by `AMiGA` for Biolog plates that are correctly named for `AMiGA` to recognize them. If you are not analyzing `Biolog` plates, you will have to pass a mapping or `mapping\meta.txt` file to communicate with `AMiGA`. See [Preparing Metadata](/amiga/doc/metadata.html) for more details.

The proper syntax for the argument is to define the variable of interest (`Isolate`) followed by a colon (`:`) followed by the values of the variable of interest separated by commmas (`,`).

The summary results are merged into a single file with a name that includes a time tamp `summary_{Year}-{Month}-{Day}_{Hour}-{Minutes}-{Seconds}.txt`. However, if you pass the `-o` argument, you can give the file a unique name instead of a time stamp.

<br />

**Example Two**

Same as above but you also  want to analyze these isolates when only grown on a select set of substrates.

```bash
python amiga.py -i /Users/firasmidani/experiments -s Isolate:CD_treA,CD_treX;Substrate:alpha-D-Glucose,D-Fructose,D-Trehalose
```

If you are selecting on more than a single variable, you must separate your selections with a semi-colon (';').

<br />

**Example Three**

You have many files in your `data` folder and you pass meta-data to `AMiGA` using individual mapping and `mapping\meta.txt` file. You have included additional unique variables in your mapping files that you will use for subsetting below.

```bash
python amiga.py -i /Users/firasmidani/experiments -s Isolate:CD_treA,CD_treX;Substrate:alpha-D-Glucose,D-Fructose,D-Trehalose;Antibiotics:None,clindamycin
```

<br />

**Example Four**

Arguments can get quite lengthy. To make them easier to read/write, you can use white spaces (surrounding quotations including colons, semicolons, and commas) to visually separate the contents of the subsetting (or hypothesis) argument as long as each argument is wrapped in double quotes.

```bash
python amiga.py -i /Users/firasmidani/experiments -s "Isolate : CD_treA , CD_treX ; Substrate : alpha-D-Glucose , D-Fructose,D-Trehalose ; Antibiotics : None , clindamycin"
```

<br />

**Example Five**

You can also specify wells that should not be analyzed. This can only be applied if you point to well locations in specific plates with the `--f` or `--flag` argument.

```bash
python amiga.py -i /Users/firasmidani/experiments --f CD_treA.txt:G7,H12;ER1_PM2-1:C3,C4,C5
```

This is often useful if you noticed, by visual checking of figures, that certain wells did not show any growth or showed odd measurements (e.g. gas bubbles can cause sharp spikes in OD measurements).

<br />

**TROUBLESHOOTING**

If you get a ```TypeError: reduce() of empty sequence with no initial value```, check your arguments for any typos. `AMiGA` is case-sensitive; for example, `Substraet:alpha-D-glucose` will result in an error because the substrate in the meta-data may be capitalized differently as `Substrate:alpha-D-Glucose`.