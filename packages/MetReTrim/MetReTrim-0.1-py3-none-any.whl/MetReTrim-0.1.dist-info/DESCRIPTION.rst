# MetReTrim

**Mohak Sharda**   
**v0.1**

***mohaks@ncbs.res.in***  
***sharda.mohak@gmail.com***

MetReTrim is a pipeline, written in python, for trimming heterogeneity 'N' spacers from the pre-processed reads given the primer sequences. It locates the primer sequence provided by a user in a given read and trims any length of the heterogenous spacer sequence towards the 5' end of the primer. It can be used for single-end and/or paired-end sequencing data.

##Installation

MetReTrim has been tested to work with the latest versions of Python 2 and Python 3. It only requires python to be installed on the system.

Users can check the version of python on their system using the following command via terminal:

```bash
python --version
```

####Installation via pip


The current version of MetReTrim can be installed using the pip command on the terminal with the following syntax:

For python version 2,

```bash
sudo python -m pip install MetReTrim
```

For python version 3,

```bash
sudo python3 -m pip install MetReTrim
```


In case pip is not installed on the system, it can installed using the following command:

For python version 2,

```bash
sudo apt install python-pip
```

For python version 3,

```bash
sudo apt install python3-pip
```


####Manual Installation

In case installation via pip doesn't work, users can download the MetReTrim executable directly from the github link: https://github.com/Mohak91/MetReTrim
Please make sure the executable is either in $PATH or users run the command line version of the executable from within the folder where it is present.

####Installing dependencies

MetReTrim requires the following python packages to be installed for a successful run:

+ os
+ sys
+ subprocess
+ getopt
+ re
+ regex

Usually, all the above mentioned packages are pre-installed in all the python versions.

However regex needs to be installed separately on the system. It can be done using the following command:

For python version 2,

```bash
python -m pip install regex
```

For python version 3,

```bash
python3 -m pip install regex
```

##Running MetReTrim

####Input

MetReTrim can be run as a command line tool on the terminal. It requires the following inputs to run:

+ Complete path of the folder containing the unprocessed fastq files in a .fastq.gz or .fastq format.
+ Complete path of the desired folder where the users wish the processed files to be stored.
+ Primer sequence(s) used in the experiment.

In case the users wish to keep the processed files in the same folder as the unprocessed files, the output folder path is not required.

By default, MetReTrim allows upto 3 mismatches in the primer sequence(s) provided by the user when locating it in the reads. This can be changed according to the user using the -m option. (See below)

By default, MetReTrim retains the primer sequence and just trims the heterogenous 'N' spacer sequence in the processed reads. Users can trim the primer sequence as well using the -k option. (See below)

####Output

MetReTrim creates two sets of output files for a given .fastq file - trimmed and untrimmed. The trimmed fastq file will contain the reads where the heterogenous 'N' spacer sequence has been removed. The untrimmed fastq file will contain those reads for which the primer sequence provided couldn't be located on the reads and therefore couldn't be processed.

####Examples

0) If MetReTrim has been installed via pip or the executables are present in the global path $PATH, the command can be run directly with the name of the executable. For example, if want to check the usage, users can type:

```bash
MetReTrim -h
```

If users have downloaded the script from github (as mentioned above) and the script is being run from the folder where it is present, the command of the usage would be as follows:

```bash
./MetReTrim -h
```


1) Running MetReTrim for single end reads:

```bash
MetReTrim -i /abc/xyz/test/fastq -o /abc/xyz/test/output -p AATTTGCGATCGAGTCTAATCGAG
```

where,  '/abc/xyz/test/fastq' is the directory where all the pre-processed fastq files are present,
	'/abc/xyz/test/output' is the directory where all the processed fastq files will be stored after trimming,
	'AATTTGCGATCGAGTCTAATCGAG is the primer sequence used for single-end sequencing.

2) Running MetReTrim for paired end reads:

```bash
MetReTrim -i /abc/xyz/test/fastq -o /abc/xyz/test/output -f AATTTGCGATCGAGTCTAATCGAG -r ATCGACTGAGCATTATATTACGCG
```

where,  '/abc/xyz/test/fastq' is the directory where all the pre-processed fastq files are present,
        '/abc/xyz/test/output' is the directory where all the processed fastq files will be stored after trimming,
        'AATTTGCGATCGAGTCTAATCGAG' is the forward primer sequence used for paired-end sequencing,
	'ATCGACTGAGCATTATATTACGCG' is the reverse primer sequence used for paired-end sequencing.

Note: Paired-end reads should be segregated in two files - forward primer and reverse primer reads respectively.

3) Running MetReTrim for both single and paired-end reads together :

```bash
MetReTrim -i /abc/xyz/test/fastq -o /abc/xyz/test/output -p ACACACACTAGGCTACGTATGCCA -f AATTTGCGATCGAGTCTAATCGAG -r ATCGACTGAGCATTATATTACGCG
```

where,  '/abc/xyz/test/fastq' is the directory where all the pre-processed fastq files are present,
	'/abc/xyz/test/output' is the directory where all the processed fastq files will be stored after trimming,
	'AATTTGCGATCGAGTCTAATCGAG' is the forward primer sequence used for paired-end sequencing,
	'ATCGACTGAGCATTATATTACGCG' is the reverse primer sequence used for paired-end sequencing.
	'ACACACACTAGGCTACGTATGCCA' is the primer sequence used for single-end sequencing

4) Running MetReTrim for paired end reads and also removing the primer sequences along with the heterogenous 'N' spacer sequences:

```bash
MetReTrim -i /abc/xyz/test/fastq -o /abc/xyz/test/output -f AATTTGCGATCGAGTCTAATCGAG -r ATCGACTGAGCATTATATTACGCG -k unkeep
```

5) 4) Running MetReTrim for paired end reads and allowing upto 5 mismatches (default: 3) in the primer sequence while locating in the reads:

```bash
MetReTrim -i /abc/xyz/test/fastq -o /abc/xyz/test/output -f AATTTGCGATCGAGTCTAATCGAG -r ATCGACTGAGCATTATATTACGCG -m 5
```


