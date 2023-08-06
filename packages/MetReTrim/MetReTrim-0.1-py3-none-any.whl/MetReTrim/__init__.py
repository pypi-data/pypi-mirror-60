#!/usr/bin/python

"""This script takes an input folder containing fastq or fastq.gz files and primer(s) sequence(s) either paired-end or single-end or both
trims the reads with respect to the primer sequence(s). The output files can put in the input folder or a separate folder can be created."""

import os
import re
import sys
import getopt
import subprocess
import regex

def assign_command_line_args_as_variables(argv):
	in_folder = ''; out_folder = '';
	primer = ''; primer1= ''; primer2=''; keep="keep"; mismatch="3";

	if len(argv)==0:
		print_usage_message()
		

	try:opts, args = getopt.getopt(argv,"hi:o:f:r:p:k:m:",["ifolder=","ofolder=","primer1=","primer2=","primer=","keep=","mismatch="])
	except getopt.GetoptError:print_usage_message()

	for opt, arg in opts:
		if opt == '-h':print_usage_message()
		elif opt in ("-i", "--ifolder"):in_folder = arg
		elif opt in ("-o", "--ofolder"):out_folder = arg
		elif opt in ("-f", "--primer1"):primer1 = arg.strip()
		elif opt in ("-r", "--primer2"):primer2 = arg.strip()
		elif opt in ("-p", "--primer"):primer = arg.strip()
		elif opt in ("-k","--keep"):keep = arg.strip()
		elif opt in ("-m","--mismatch"):mismatch = arg.strip()

	return in_folder,out_folder,primer,primer1,primer2,keep,mismatch

def prepare_non_empty_primer_list_to_trim(in_folder,out_folder,primer,primer1,primer2):
		if len(primer)!=0:
				if len(primer1)==0 and len(primer2)==0:l_primer=[primer]
				elif len(primer1)!=0 and len(primer2)!=0:l_primer=[primer1,primer2,primer]
		else:l_primer=[primer1,primer2]

		return l_primer

def make_trimmed_directory(out_folder):
		"""if an output directory doesn't exist, it will make a directory with the desired path provided"""
		if not os.path.exists(out_folder):
				print("creating the desired output directory...\n")
				mkdir="mkdir %s"%out_folder
				os.system(mkdir)

def unzip_file(in_folder):
		"""checks if fastq files are in a compressed format. If it is, then this function extracts the file in the same folder"""
		for file_name in os.listdir(in_folder):
				if file_name.endswith(".gz"):
						os.system("gunzip %s/%s"%(in_folder,file_name))
				else:
						pass

def trim_reads(in_folder,out_folder,l_primer,keep,mismatch):
	"""detects the appropriate primer sequence and trims the read sequence before the start of the primer sequence"""
	for fastq_file in os.listdir(in_folder):
		if not fastq_file.endswith("_trimmed.fastq") and not fastq_file.endswith("_untrimmed.fastq"):
			check=check_fastq(in_folder,fastq_file)
			if not check:continue
			primer=detect_primer(in_folder,fastq_file,l_primer)
			trimmed_file,untrimmed_file=make_trimmed_filename(fastq_file)
			read_fastq_process_write_output(in_folder,fastq_file,out_folder,trimmed_file,untrimmed_file,primer,keep,mismatch)

def read_fastq_process_write_output(in_folder,fastq_file,out_folder,trimmed_file,untrimmed_file,primer,keep,mismatch):
	with open("%s/%s"%(in_folder,fastq_file)) as fh, open("%s/%s"%(out_folder,trimmed_file),"w") as f, open("%s/%s"%(out_folder,untrimmed_file),"w") as w:
		while True:
			info=fh.readline().strip() 
			seq=fh.readline().strip()
			plus=fh.readline().strip()
			qual=fh.readline().strip()
			if len(info)==0:break
			trimmed_seq,trimmed_qual,untrimmed_seq,untrimmed_qual=seq_process(seq,qual,primer,keep,mismatch)
			if len(trimmed_seq)!=0:f.write("%s\n%s\n%s\n%s\n"%(info,trimmed_seq,plus,trimmed_qual))
			if len(untrimmed_seq)!=0:w.write("%s\n%s\n%s\n%s\n"%(info,untrimmed_seq,plus,untrimmed_qual))

	remove_empty_file(out_folder,[trimmed_file,untrimmed_file])
		
def check_fastq(in_folder,fastq_file):
	"""check if the file format is fastq"""
	if fastq_file.endswith(".fastq"):
		with open("%s/%s"%(in_folder,fastq_file)) as fh:
			num_lines=len(fh.readlines())
		if num_lines%4==0:
			return True
		else:
			print("%s file doesn't have equal number of fastq lines.\nSkipping this file...\n"%fastq_file)
			return False 

	else:
		print("%s doesn't seem to be a fastq file. Please check the format and run this file again.\nSkipping this file...\n"%fastq_file)
		return False

def detect_primer(in_folder,fastq_file,l_primer):
		"""Detects which primer is to be used: if single end, return the only primer; if paired end, returns either forward read or reverse primer"""

		if len(l_primer)==0:
				print("please provide the primer sequence(s)...\nExiting...\n")
				sys.exit(2)
		elif len(l_primer)==1:
				read_type=int(detect_read_type(in_folder,fastq_file))-1
				if read_type==3:
						primer=process_primer(l_primer[0])
				else:
						print("please provide the correct primer sequence...\nExiting...\n")
						sys.exit(2)
		elif len(l_primer)==2:
				read_type=int(detect_read_type(in_folder,fastq_file))-1
				primer=process_primer(l_primer[read_type])
		elif len(l_primer)==3:
				read_type=int(detect_read_type(in_folder,fastq_file))-1
				primer=process_primer(l_primer[read_type])

		if len(primer)==0:
				print("please provide the correct primer sequence...\nExiting...\n")
				sys.exit(2)

		return primer

def detect_read_type(in_folder,fastq_file):
		"""detects if forward read or reverse read or single-end read"""
		read_type=0
		with open("%s/%s"%(in_folder,fastq_file)) as m:
				while True:
						info=m.readline()
						if len(info.split(" "))>1:
								read_type=info.split(" ")[1].split(":")[0]
								return read_type
						else:
								read_type="3"
								return read_type

def process_primer(crude_primer):
		"""prepares a regular expression to incorporate the ambiguous nucleotide characters for searching across the reads"""
		primer=""
		nucleotide_dict={"A":"A","T":"T","G":"G","C":"C","R":"(G|A)","Y":"(C|T)","W":"(A|T)","K":"(G|T)","M":"(A|C)","S":"(G|C)","B":"(G|T|C)","D":"(G|A|T)","H":"(A|C|T)","V":"(G|C|A)","N":"(A|G|C|T)"}
		for nucleotide in crude_primer:
				primer=primer+nucleotide_dict[nucleotide]

		return primer
	
def make_trimmed_filename(fastq_file):
	"""prepare filenames to be used for trimmed and untrimmed files"""
	trimmed_file=fastq_file[:-6]+"_trimmed.fastq"
	untrimmed_file=fastq_file[:-6]+"_untrimmed.fastq"
	return trimmed_file,untrimmed_file

def include_errors_primers(primer,seq,mismatch):
	"""incorporates mismatches and locates the primer on a sequence"""
	mismatch_int=int(mismatch)
	regex_list=regex.findall("(%s){s<=%d}"%(primer,mismatch_list),seq)
	#print seq,regex_list
	if not len(regex_list)==0:
		primer=regex_list[0][0]
		primer_search=re.search(primer,seq)
	else:
		primer_search=None

	return primer_search,primer,regex_list
			
def seq_process(seq,qual,primer,keep,mismatch):
	"""Finds the index of the primer position in the read and trims everything before it."""
	trimmed_seq="";trimmed_qual="";untrimmed_seq="";untrimmed_qual=""
	
	primer_search,primer,regex_list=include_errors_primers(primer,seq,mismatch)

	if primer_search:
		primer_index=primer_search.start()
		if keep=="keep":
			trimmed_seq=seq[primer_index:]
			#print seq,regex_list,trimmed_seq
			trimmed_qual=qual[primer_index:]
		elif keep=="unkeep":
			unkeep_index=primer_index+len(primer)
			trimmed_seq=seq[unkeep_index:]
			trimmed_qual=qual[unkeep_index:]
	else:
		untrimmed_seq=seq
		untrimmed_qual=qual

	return trimmed_seq,trimmed_qual,untrimmed_seq,untrimmed_qual

def remove_empty_file(out_folder,file_list):
		for file_name in file_list:
				if os.stat("%s/%s"%(out_folder,file_name)).st_size == 0:
						print(" Removing ",file_name)
						os.remove("%s/%s"%(out_folder,file_name))

def print_usage_message():
	print("usage: ./metretrim [OPTIONS] -i INPUT -o OUTPUT -p PRIMER_SINGLE_END -f PRIMER_FORWARD -r PRIMER_REVERSE\n\nTrim heterogenous 'N' spacer sequences from the 5' end of the pre-processed reads.\n\npositional arguments:\n\n-i, --ifolder\n\tTakes INPUT folder path. INPUT contains the fastq files to be processed.\n\tFastq files can be in a .fastq format or .fastq.gz format.\n\tIn case an output folder is not provided, the processed files will be created in INPUT.\n\n-o, --ofolder\n\tTakes OUTPUT folder path as the desired directory to store the processed reads.\n\tIn case OUTPUT doesn't already exist, the program creates OUTPUT first and then stores the processed files.\n\n-p, --primer\n\tTakes PRIMER_SINGLE_END sequence if the read files have a single end sequencing read data.\n\n-f, --primer1\n\tTakes PRIMER_FORWARD sequence as the forward primer sequence if the read files have a paired end sequencing read data.\n\n-r, --primer2\n\tTakes PRIMER_REVERSE sequence as the reverse primer sequence if the read files have a paired end sequencing read data.\n\n\noptional arguments:\n\n-h\n\tShows this help message and exit\n\n-k, --keep\n\tControls if primer sequence needs to be trimmed along with the 'N' heterogenous spacer sequence\n\tIt can take either of the two options: 1) -k keep or, 2) -k unkeep\n\tDefault: -k keep (retains the primer sequence in the reads)\n\n-m, --mismatch\n\tControls the number of mismatches to be allowed in the primer sequence(s) while locating them in the reads to be processed\n\tDefault: -m 3 (locates primer sequences in the reads to be processed by allowing upto 3 mismatches)\n\nNOTE:\n\n1) In case the input folder has both single-end and paired-end read files, all the three -f -r and -p primer sequence options are required.\n2) If using paired end reads, make sure the forward reads and reverse reads are segregated into two files.\n3) Please provide the full and correct paths of the input and output folders.\n\nHappy Trimming!! :)\n")
	sys.exit(2)

def main(argv):
	"""Takes the command line argument list excluding the python executable file name and trims the reads."""
	
	in_folder,out_folder,primer,primer1,primer2,keep,mismatch=assign_command_line_args_as_variables(argv)   
	
	try:
		if len(out_folder)==0:out_folder=in_folder
		l_primer=prepare_non_empty_primer_list_to_trim(in_folder,out_folder,primer,primer1,primer2)
		try:
			make_trimmed_directory(out_folder)
			unzip_file(in_folder)
			trim_reads(in_folder,out_folder,l_primer,keep,mismatch)
		except OSError:print_usage_message()
	except IOError:print_usage_message()

if __name__ == "__main__":
	main(sys.argv[1:])
