#!/usr/bin/python
#-*- coding: utf-8 -*-
from tkinter import *
import tkinter as tk
import tkinter.messagebox
import tkinter.filedialog
import subprocess
import shutil,os,re
import multiprocessing
import configparser
root=Tk()
root.title("KinomeRun")
KINOMERENDER=""
PLIP=""
KINASE_DB=""
LIGAND=""
WORKING=""
Numcpu=""
joobs=""
EXHAUSTIVENESS=""
analysisworking=""
HPC='NO'
def run_screening():
	global HPC
	if PARALLEL_check.get() == 0: 
		tkinter.messagebox.showinfo("Warning","GNU Parallel not found!",parent=root)
		return
	if VINA_check.get() == 0:
		tkinter.messagebox.showinfo("Warning","AutoDock Vina not found!",parent=root)
		return
	if PLIP_check.get() == 0:
		tkinter.messagebox.showinfo("Warning","PLIP not found!",parent=root)
		return
	if KINDB_check.get() == 0:
		tkinter.messagebox.showinfo("Warning",'KinaseDB not found!',parent=root)
		return
	global joobs
	joobs=0
	run_scr=Toplevel(root)
	def get_ligdir():
		global LIGAND
		filen= tkinter.filedialog.askdirectory(initialdir="~",title="Enter the directory containing ligands",parent=run_scr)
		if filen:
			if ' ' in filen:
				tkinter.messagebox.showinfo("Warning!", "Whitespace found in the specified directory!\nKindly remove the whitespace in directoy naming", parent=run_scr)
				return
			else:
				if os.path.exists(filen):
					LIGAND=filen
		else:
			tkinter.messagebox.showinfo("Warning!", "File directory not specified!", parent=run_scr)
			return
	def get_workdir():
		global WORKING
		filen= tkinter.filedialog.askdirectory(initialdir="~",title="Enter the working directory",parent=run_scr)
		if filen:
			if ' ' in filen:
				tkinter.messagebox.showinfo("Warning!", "Whitespace found in the specified directory!\nKindly remove the whitespace in directoy naming", parent=run_scr)
				return
			else:
				if os.path.exists(filen):
					temp=os.listdir(filen)
					if temp:
						tkinter.messagebox.showinfo("Warning", "Working Directory is not empty!", parent=run_scr)
						return
					else:
						WORKING=filen
		else:
			tkinter.messagebox.showinfo("Warning!", "File directory not specified!", parent=run_scr)
			return	
	Label(run_scr,bg="white",text="Provide Ligand \n containg directoy",relief=SOLID,font=("Arial",15,'bold'),width=20,height=2,justify=CENTER).grid(row=0,column=0,sticky=W+E+N+S)
	Button(run_scr,bg="gold",text="<Open>",relief=RAISED,borderwidth=3,font=("Arial",15,'bold'),width=10,height=2,command=get_ligdir).grid(row=0,column=1,sticky=W+E+N+S)
	Ncpu=multiprocessing.cpu_count()
	Label(run_scr,bg="white",text=str(Ncpu)+" number of CPU processors \n detected in your system",relief=SOLID,font=("Arial",15,'bold'),width=20,height=2,justify=CENTER).grid(row=1,column=0,columnspan=2,sticky=W+E+N+S)
	Label(run_scr,bg="white",text="Enter the number of CPU \n for running a single vina job :",relief=SOLID,font=("Arial",15,'bold'),width=30,height=2,justify=CENTER).grid(row=2,column=0,sticky=W+E+N+S)
	global Numcpu
	Numcpu=StringVar()
	Numcpu.set(8)
	joobs=int(Ncpu/int(Numcpu.get()))
	if joobs:
		Label(run_scr,bg="white",text= str(int(Ncpu/int(Numcpu.get())))+" Jobs will run in parallel",relief=SOLID,font=("Arial",15,'bold'),width=30,height=2,justify=CENTER).grid(row=3,column=0,columnspan=2,sticky=W+E+N+S)
	Entry(run_scr,bd=5,textvariable=Numcpu,font=("Arial",15,'bold'),justify=CENTER).grid(row=2,column=1,sticky=W+E+N+S)
	def checkback(*args):
		for f in Numcpu.get():
			if f not in '1234567890' :
				tkinter.messagebox.showinfo("Warning","Please provide the integer Values!",parent=run_scr)
				return
		global joobs
		joobs=0
		if len(Numcpu.get()) > 0:
			if int(Numcpu.get()) > Ncpu or int(Numcpu.get()) == 0 :
				tkinter.messagebox.showinfo("Warning","Please provide the values less than "+str(Ncpu)+"!",parent=run_scr)
				print('hello')
				return
			else:
				Label(run_scr,bg="white",text= str(int(Ncpu/int(Numcpu.get())))+" Jobs will run in parallel",relief=SOLID,font=("Arial",15,'bold'),width=30,height=2,justify=CENTER).grid(row=3,column=0,columnspan=2,sticky=W+E+N+S)
			joobs=int(Ncpu/int(Numcpu.get()))
		else:
			Label(run_scr,bg="white",text= "0 Jobs will run in parallel",relief=SOLID,font=("Arial",15,'bold'),width=30,height=2,justify=CENTER).grid(row=3,column=0,columnspan=2,sticky=W+E+N+S)
	Numcpu.trace('w',checkback)
	Label(run_scr,bg="white",text="Enter the exhaustiveness:",font=("Arial",15,"bold"),relief=SOLID,width=30,height=3).grid(row=4,column=0,sticky=E+W+N+S)
	Exhaust=StringVar()
	Entry(run_scr,bd=5,textvariable=Exhaust,font=("Arial",15,'bold'),justify=CENTER).grid(row=4,column=1,sticky=W+E+N+S)
	def ex_checkback(*args):
		if Exhaust.get():
			for f in Exhaust.get():
				if f not in '1234567890' :
					tkinter.messagebox.showinfo("Warning","Please provide the integer Values!",parent=run_scr)
					return
			global EXHAUSTIVENESS
			EXHAUSTIVENESS=int(Exhaust.get())
	Exhaust.trace('w',ex_checkback)
	def run_script_out():
		global LIGAND
		global WORKING
		global EXHAUSTIVENESS
		global joobs
		global KINASE_DB
		global PLIP
		if HPC == 'YES':
			WORKING=os.getcwd()
			LIGAND=''
			KINASE_DB=''
			PLIP=''
			EXHAUSTIVENESS=0
			joobs=0
#			Numcpu.set(0)
		elif HPC == 'NO':
			if not LIGAND:
				tkinter.messagebox.showinfo("Warning","Please provide the Ligand directory!",parent=run_scr)
				return
			if not WORKING:
				tkinter.messagebox.showinfo("Warning","Please provide the Working directory!",parent=run_scr)
				return
			for f in Numcpu.get():
				if f not in '1234567890':
					tkinter.messagebox.showinfo("Warning", "Please provide the integer Values!", parent=run_scr)
					return
			if len(Numcpu.get()) > 0:
				if int(Numcpu.get()) > Ncpu or int(Numcpu.get()) == 0:
					tkinter.messagebox.showinfo("Warning", "Please provide the values less than " + str(Ncpu) + "!",parent=run_scr)
					return
			if not Numcpu.get() or joobs == 0:
			    tkinter.messagebox.showinfo("Warning", "Please provide the number of CPU's to run parallel!", parent=run_scr)
			    return
			if not EXHAUSTIVENESS:
			    tkinter.messagebox.showinfo("Warning", "Please provide the Exhaustiveness value!", parent=run_scr)
			    return
			if not KINASE_DB:
			    tkinter.messagebox.showinfo("Warning", "Please provide the KINASE DB directory!", parent=run_scr)
			    return
		BASH_SCRIPT='''
#!/bin/bash
LIGAND="%s"	# Ligand directory
WORKING="%s"	# Working directory 
KINASE_DB="%s"	# Kinase database directory
PLIP="%s"	# PLIP directory
ex="%d"		# Exhaustiveness
numcpu="%d"	# Number of CPU's for single vina job
joobs="%d"	# Number of jobs to run in parallel
HPC="%s"''' % (LIGAND,WORKING,KINASE_DB,PLIP,EXHAUSTIVENESS,int(Numcpu.get()),joobs,HPC)
		BASH_SCRIPT+='''
echo -e "KinomeRun - Virtual screening Module:"
echo -e "==============================================================================="
echo " Ligand directory:"$LIGAND""
echo " Protein directory:"$KINASE_DB"/receptor"
echo " Working directory:"$WORKING""
echo " Exhaustiveness: "$ex""
echo " Number of CPU for running one Vina job: "$numcpu""
echo -e " Number of VINA jobs to run in parallel:"$joobs""
echo -e "===============================================================================\\n"
echo -e "Enter\\n[1] To accept these parameters\\n[2] To exit"
i=1
while [ "$i" -ge 0 ]
do
	if [ "$HPC" == 'NO' ]
	then
		read -ep ">>>" skippara
	else
		skippara=1
	fi
	if [ "$skippara" == 1 ]
	then
		break
	elif [ "$skippara" == 2 ]
	then
		exit
	else
		echo -e "Empty return. Type again"
		i=`expr $i + 1`
	fi
done
clear
cd $WORKING; # mkdir Combined_Results
echo -e "\\n-------------------------------------------------------------------------------\\n---------------------------------Summary Report--------------------------------\\n-------------------------------------------------------------------------------\\nLigand Input Directory="$LIGAND"\\nReceptor Input Directory="$KINASE_DB"/receptor\\nWorking directory="$WORKING"\\nThe number of ligand complex needed to be generated after VS:"$top"\\n" >>"$WORKING"/summary.txt
## Space check and file renaming##
cd "$LIGAND"; ls -1 | grep 'pdbqt' >spacecheck.txt
spacecheck=`sed -n "/\s/p" spacecheck.txt`
if [ -n "$spacecheck" ]
then
	echo -e "~~Space detected in the ligand files~~~\\nSpace will be replaced by _ in the filename"
	sed -n "/\s/p" spacecheck.txt >spacefiles.txt
	echo -n "
	#!/bin/bash
	bspace=\`echo \\"\$1\\" | sed \\"s/\s/_/g\\"\` 
	mv \\"\$1\\" \\"\$bspace\\"" >rename.bash
	if [ "$HPC" == "YES" ]
	then
		cat spacefiles.txt | grep "pdbqt" | parallel -j "$joobs" --no-notice --eta "bash rename.bash {}" 2>/dev/null
	else:
		cat spacefiles.txt | grep "pdbqt" | parallel -j "$joobs" --no-notice --eta "bash rename.bash {}"
	fi
	rm rename.bash spacefiles.txt
else
	:
fi
rm spacecheck.txt; cd "$LIGAND"; ls -1 | grep 'pdbqt' >ligand_list.txt; sed -i "s/.pdbqt//g" ligand_list.txt
##### Creating Ligand directories #############		
cd "$LIGAND"
while read -r l
do
	cd "$WORKING"; mkdir "$l" ; cd "$l" ; mkdir docked_files Results; cd docked_files; mkdir pdbqt_out pdbqt_txt plip_temp;
	cp "$LIGAND"/"$l".pdbqt "$WORKING"/"$l"/docked_files/
	cd "$WORKING"/"$l"/docked_files/plip_temp
	echo -n "
import sys
asd=open(sys.argv[1],'r')
FILE1=asd.readlines()
asd.close()

for f in FILE1:
	if f[0:4].strip() in [ 'ATOM', 'HETATM' ]:
		print(f[17:20].strip())
		break" >"$WORKING"/"$l"/docked_files/plip_temp/ligname.py
	echo -n "
	#!/bin/bash
	cd plip_temp; mkdir \${1%.pdbqt}; cd \${1%.pdbqt}
	while read -r ll
	do
		echo \\"\$ll\\" >>temp.pdbqt
		if [ \\"\$ll\\" == 'ENDMDL' ]
		then
			LIGNAME=\$(python ../ligname.py temp.pdbqt)
			cut -c-66 ../../\\"\$1\\" >\${1%.pdbqt}.pdb;
			sed '/ROOT/d;/ENDROOT/d;/BRANCH/d;/ENDBRANCH/d;/TORSDOF/d' temp.pdbqt | cut -c-66 >>\${1%.pdbqt}.pdb
			"$PLIP"/plipcmd.py -f \${1%.pdbqt}.pdb -x --name \${1%.pdbqt}
			python "$KINASE_DB"/xmltree_KLIFS.py \${1%.pdbqt}.xml \$(grep 'MODEL' temp.pdbqt| awk '{print \$2}') \$(grep 'RESULT' temp.pdbqt| awk '{print \$4}') \\"\$LIGNAME\\" "$KINASE_DB" >>../../../Results/\\"\$2\\".txt
			rm *.pdb temp.pdbqt \${1%.pdbqt}.xml
		fi
	done <../../pdbqt_out/\\"\$1\\"
	cd ..; rmdir \${1%.pdbqt}" >"$WORKING"/"$l"/docked_files/plip_temp/plip.bash
	echo -e ""$l" file created and respective protein and configuration file moved\\n\\n"
	echo -e "Ligand "$l" is in the "$l" directory\\n" >>"$WORKING"/summary.txt	
	clear
done <ligand_list.txt
####Virutal screnning###
cd "$LIGAND"
time=`date +"%c"`; echo -e "Virtual screening start time : "$time"\\n" >>"$WORKING"/summary.txt
while read -r l
do
	echo -e " ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	echo -e " + KinomeRun - Virtual screening:                                           +"
	echo -e " + -----------------------------                                            +"
	echo -e " + Multiple protein Virtual screening using Autodock Vina: Running...       +"
	echo -e " + 	* Parallel Docking            : Running...                          +"
	echo -e " ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	echo -e "\\n"
	cd "$KINASE_DB"/receptor
	echo -e "~~~~~Running Autodock Vina virtual screening for "$l"~~~~~~\\n\\n"
	if [ "$HPC" == "YES" ]
	then
		ls -1U | grep 'pdbqt' | parallel -j "$joobs" --no-notice --eta " cd "$WORKING"/"$l"/docked_files/ ; cp "$KINASE_DB"/receptor/{} . ;cp "$KINASE_DB"/receptor/{.}.txt .; vina --config {.}.txt --receptor {} --ligand "$l".pdbqt --exhaustiveness "$ex" --cpu "$numcpu" --out pdbqt_out/{} --log pdbqt_txt/{.}.txt >"$WORKING"/log_running.txt; bash plip_temp/plip.bash {} "$l";rm {} {.}.txt" 2>/dev/null
	else
		ls -1U | grep 'pdbqt' | parallel -j "$joobs" --no-notice --eta " cd "$WORKING"/"$l"/docked_files/ ; cp "$KINASE_DB"/receptor/{} . ;cp "$KINASE_DB"/receptor/{.}.txt .; vina --config {.}.txt --receptor {} --ligand "$l".pdbqt --exhaustiveness "$ex" --cpu "$numcpu" --out pdbqt_out/{} --log pdbqt_txt/{.}.txt >"$WORKING"/log_running.txt; bash plip_temp/plip.bash {} "$l";rm {} {.}.txt"
	fi	
	clear
done <ligand_list.txt
cd "$LIGAND"
while read -r l
do
	rm "$WORKING"/"$l"/docked_files/"$l".pdbqt
	rm "$WORKING"/"$l"/docked_files/plip_temp/ligname.py
	rm "$WORKING"/"$l"/docked_files/plip_temp/plip.bash
	rmdir "$WORKING"/"$l"/docked_files/plip_temp
done <ligand_list.txt
cd "$LIGAND"; rm ligand_list.txt
cd "$WORKING"; rm log_running.txt
clear
echo -e " ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo -e " + KinomeRun - Virtual screening:                                           +"
echo -e " + -----------------------------                                            +"
echo -e " + Multiple protein Virtual screening using Autodock Vina: Running...       +"
echo -e " + 	* Parallel Docking            : Completed                           +"
echo -e " ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo -e "-----KinomeRun VS finished------"
time=`date +"%c"`; echo -e "Virtual screening end time : "$time"\\n" >>"$WORKING"/summary.txt
echo "
If you used ReverseKinase in your work, please cite: 

Samdani, A. and Vetrivel, U. (2018)." >>"$WORKING"/summary.txt''' 
		asd=open(WORKING+'/KinomeRun.bash','w')
		asd.write(BASH_SCRIPT)
		asd.close()
		root.destroy()
	Label(run_scr,bg="white",text="Provide Working directoy",relief=SOLID,font=("Arial",15,'bold'),width=20,height=2,justify=CENTER).grid(row=5,column=0,sticky=W+E+N+S)
	Button(run_scr,bg="gold",text="<Open>",relief=RAISED,borderwidth=3,font=("Arial",15,'bold'),width=10,height=2,command=get_workdir).grid(row=5,column=1,sticky=W+E+N+S)
	HPC_check=IntVar()
	def hpc_checkback(*args):
		global HPC
		if HPC_check.get() == 1:
			HPC="YES"
		elif HPC_check.get() == 0:
			HPC="NO"
	HPC_check.trace('w',hpc_checkback)
	Checkbutton(run_scr,text="HPC script",bg="white",variable=HPC_check,font=("Arial",15,'bold'),offvalue=0,onvalue=1).grid(row=6,column=0,columnspan=2,sticky=W+E+N+S)
	Button(run_scr,bg="green2",fg="black",text="Run!!",relief=RAISED,borderwidth=3,font=("Arial",15,'bold'),width=10,height=2,command=run_script_out).grid(row=7,column=0,columnspan=2,sticky=W+E+N+S)

#~~~~ For analysis ~~~~~~~~
def run_analysis():
	if KIN_check.get() == 0:
		tkinter.messagebox.showinfo("Warning","Kinome-Render not found!",parent=root)
		return
	if KINDB_check.get() == 0:
		tkinter.messagebox.showinfo("Warning",'KinaseDB not found!',parent=root)
		return
	analysis_scr=Toplevel(root)
	filename=""
	filedir=""
	global Analysiscount
	Analysiscount=1
	GENE=""
	#~~~~ INITIALIZATION ~~~~~~~~~~~~~~~~
	HBD_1=IntVar();HBA_1=IntVar();HYDRO_1=IntVar();PIPIT_1=IntVar();PIPIP_1=IntVar();PICAT_1=IntVar();POSITIVE_1=IntVar();NEGATIVE_1=IntVar();HALOGEN_1=IntVar()
	HBD_2=IntVar();HBA_2=IntVar();HYDRO_2=IntVar();PIPIT_2=IntVar();PIPIP_2=IntVar();PICAT_2=IntVar();POSITIVE_2=IntVar();NEGATIVE_2=IntVar();HALOGEN_2=IntVar()
	HBD_3=IntVar();HBA_3=IntVar();HYDRO_3=IntVar();PIPIT_3=IntVar();PIPIP_3=IntVar();PICAT_3=IntVar();POSITIVE_3=IntVar();NEGATIVE_3=IntVar();HALOGEN_3=IntVar()
	HBD_4=IntVar();HBA_4=IntVar();HYDRO_4=IntVar();PIPIT_4=IntVar();PIPIP_4=IntVar();PICAT_4=IntVar();POSITIVE_4=IntVar();NEGATIVE_4=IntVar();HALOGEN_4=IntVar();
	HBD_5=IntVar();HBA_5=IntVar();HYDRO_5=IntVar();PIPIT_5=IntVar();PIPIP_5=IntVar();PICAT_5=IntVar();POSITIVE_5=IntVar();NEGATIVE_5=IntVar();HALOGEN_5=IntVar();
	HBD_6=IntVar();HBA_6=IntVar();HYDRO_6=IntVar();PIPIT_6=IntVar();PIPIP_6=IntVar();PICAT_6=IntVar();POSITIVE_6=IntVar();NEGATIVE_6=IntVar();HALOGEN_6=IntVar();
	HBD_7=IntVar();HBA_7=IntVar();HYDRO_7=IntVar();PIPIT_7=IntVar();PIPIP_7=IntVar();PICAT_7=IntVar();POSITIVE_7=IntVar();NEGATIVE_7=IntVar();HALOGEN_7=IntVar();
	HBD_8=IntVar();HBA_8=IntVar();HYDRO_8=IntVar();PIPIT_8=IntVar();PIPIP_8=IntVar();PICAT_8=IntVar();POSITIVE_8=IntVar();NEGATIVE_8=IntVar();HALOGEN_8=IntVar();
	HBD_9=IntVar();HBA_9=IntVar();HYDRO_9=IntVar();PIPIT_9=IntVar();PIPIP_9=IntVar();PICAT_9=IntVar();POSITIVE_9=IntVar();NEGATIVE_9=IntVar();HALOGEN_9=IntVar();
	HBD_10=IntVar();HBA_10=IntVar();HYDRO_10=IntVar();PIPIT_10=IntVar();PIPIP_10=IntVar();PICAT_10=IntVar();POSITIVE_10=IntVar();NEGATIVE_10=IntVar();HALOGEN_10=IntVar();
	HBD_11=IntVar();HBA_11=IntVar();HYDRO_11=IntVar();PIPIT_11=IntVar();PIPIP_11=IntVar();PICAT_11=IntVar();POSITIVE_11=IntVar();NEGATIVE_11=IntVar();HALOGEN_11=IntVar();
	HBD_12=IntVar();HBA_12=IntVar();HYDRO_12=IntVar();PIPIT_12=IntVar();PIPIP_12=IntVar();PICAT_12=IntVar();POSITIVE_12=IntVar();NEGATIVE_12=IntVar();HALOGEN_12=IntVar();
	HBD_13=IntVar();HBA_13=IntVar();HYDRO_13=IntVar();PIPIT_13=IntVar();PIPIP_13=IntVar();PICAT_13=IntVar();POSITIVE_13=IntVar();NEGATIVE_13=IntVar();HALOGEN_13=IntVar();
	HBD_14=IntVar();HBA_14=IntVar();HYDRO_14=IntVar();PIPIT_14=IntVar();PIPIP_14=IntVar();PICAT_14=IntVar();POSITIVE_14=IntVar();NEGATIVE_14=IntVar();HALOGEN_14=IntVar();
	HBD_15=IntVar();HBA_15=IntVar();HYDRO_15=IntVar();PIPIT_15=IntVar();PIPIP_15=IntVar();PICAT_15=IntVar();POSITIVE_15=IntVar();NEGATIVE_15=IntVar();HALOGEN_15=IntVar();
	HBD_16=IntVar();HBA_16=IntVar();HYDRO_16=IntVar();PIPIT_16=IntVar();PIPIP_16=IntVar();PICAT_16=IntVar();POSITIVE_16=IntVar();NEGATIVE_16=IntVar();HALOGEN_16=IntVar();
	HBD_17=IntVar();HBA_17=IntVar();HYDRO_17=IntVar();PIPIT_17=IntVar();PIPIP_17=IntVar();PICAT_17=IntVar();POSITIVE_17=IntVar();NEGATIVE_17=IntVar();HALOGEN_17=IntVar();
	HBD_18=IntVar();HBA_18=IntVar();HYDRO_18=IntVar();PIPIT_18=IntVar();PIPIP_18=IntVar();PICAT_18=IntVar();POSITIVE_18=IntVar();NEGATIVE_18=IntVar();HALOGEN_18=IntVar();
	HBD_19=IntVar();HBA_19=IntVar();HYDRO_19=IntVar();PIPIT_19=IntVar();PIPIP_19=IntVar();PICAT_19=IntVar();POSITIVE_19=IntVar();NEGATIVE_19=IntVar();HALOGEN_19=IntVar();
	HBD_20=IntVar();HBA_20=IntVar();HYDRO_20=IntVar();PIPIT_20=IntVar();PIPIP_20=IntVar();PICAT_20=IntVar();POSITIVE_20=IntVar();NEGATIVE_20=IntVar();HALOGEN_20=IntVar();
	HBD_21=IntVar();HBA_21=IntVar();HYDRO_21=IntVar();PIPIT_21=IntVar();PIPIP_21=IntVar();PICAT_21=IntVar();POSITIVE_21=IntVar();NEGATIVE_21=IntVar();HALOGEN_21=IntVar();
	HBD_22=IntVar();HBA_22=IntVar();HYDRO_22=IntVar();PIPIT_22=IntVar();PIPIP_22=IntVar();PICAT_22=IntVar();POSITIVE_22=IntVar();NEGATIVE_22=IntVar();HALOGEN_22=IntVar();
	HBD_23=IntVar();HBA_23=IntVar();HYDRO_23=IntVar();PIPIT_23=IntVar();PIPIP_23=IntVar();PICAT_23=IntVar();POSITIVE_23=IntVar();NEGATIVE_23=IntVar();HALOGEN_23=IntVar();
	HBD_24=IntVar();HBA_24=IntVar();HYDRO_24=IntVar();PIPIT_24=IntVar();PIPIP_24=IntVar();PICAT_24=IntVar();POSITIVE_24=IntVar();NEGATIVE_24=IntVar();HALOGEN_24=IntVar();
	HBD_25=IntVar();HBA_25=IntVar();HYDRO_25=IntVar();PIPIT_25=IntVar();PIPIP_25=IntVar();PICAT_25=IntVar();POSITIVE_25=IntVar();NEGATIVE_25=IntVar();HALOGEN_25=IntVar();
	HBD_26=IntVar();HBA_26=IntVar();HYDRO_26=IntVar();PIPIT_26=IntVar();PIPIP_26=IntVar();PICAT_26=IntVar();POSITIVE_26=IntVar();NEGATIVE_26=IntVar();HALOGEN_26=IntVar();
	HBD_27=IntVar();HBA_27=IntVar();HYDRO_27=IntVar();PIPIT_27=IntVar();PIPIP_27=IntVar();PICAT_27=IntVar();POSITIVE_27=IntVar();NEGATIVE_27=IntVar();HALOGEN_27=IntVar();
	HBD_28=IntVar();HBA_28=IntVar();HYDRO_28=IntVar();PIPIT_28=IntVar();PIPIP_28=IntVar();PICAT_28=IntVar();POSITIVE_28=IntVar();NEGATIVE_28=IntVar();HALOGEN_28=IntVar();
	HBD_29=IntVar();HBA_29=IntVar();HYDRO_29=IntVar();PIPIT_29=IntVar();PIPIP_29=IntVar();PICAT_29=IntVar();POSITIVE_29=IntVar();NEGATIVE_29=IntVar();HALOGEN_29=IntVar();
	HBD_30=IntVar();HBA_30=IntVar();HYDRO_30=IntVar();PIPIT_30=IntVar();PIPIP_30=IntVar();PICAT_30=IntVar();POSITIVE_30=IntVar();NEGATIVE_30=IntVar();HALOGEN_30=IntVar();
	HBD_31=IntVar();HBA_31=IntVar();HYDRO_31=IntVar();PIPIT_31=IntVar();PIPIP_31=IntVar();PICAT_31=IntVar();POSITIVE_31=IntVar();NEGATIVE_31=IntVar();HALOGEN_31=IntVar();
	HBD_32=IntVar();HBA_32=IntVar();HYDRO_32=IntVar();PIPIT_32=IntVar();PIPIP_32=IntVar();PICAT_32=IntVar();POSITIVE_32=IntVar();NEGATIVE_32=IntVar();HALOGEN_32=IntVar();
	HBD_33=IntVar();HBA_33=IntVar();HYDRO_33=IntVar();PIPIT_33=IntVar();PIPIP_33=IntVar();PICAT_33=IntVar();POSITIVE_33=IntVar();NEGATIVE_33=IntVar();HALOGEN_33=IntVar();
	HBD_34=IntVar();HBA_34=IntVar();HYDRO_34=IntVar();PIPIT_34=IntVar();PIPIP_34=IntVar();PICAT_34=IntVar();POSITIVE_34=IntVar();NEGATIVE_34=IntVar();HALOGEN_34=IntVar();
	HBD_35=IntVar();HBA_35=IntVar();HYDRO_35=IntVar();PIPIT_35=IntVar();PIPIP_35=IntVar();PICAT_35=IntVar();POSITIVE_35=IntVar();NEGATIVE_35=IntVar();HALOGEN_35=IntVar();
	HBD_36=IntVar();HBA_36=IntVar();HYDRO_36=IntVar();PIPIT_36=IntVar();PIPIP_36=IntVar();PICAT_36=IntVar();POSITIVE_36=IntVar();NEGATIVE_36=IntVar();HALOGEN_36=IntVar();
	HBD_37=IntVar();HBA_37=IntVar();HYDRO_37=IntVar();PIPIT_37=IntVar();PIPIP_37=IntVar();PICAT_37=IntVar();POSITIVE_37=IntVar();NEGATIVE_37=IntVar();HALOGEN_37=IntVar();
	HBD_38=IntVar();HBA_38=IntVar();HYDRO_38=IntVar();PIPIT_38=IntVar();PIPIP_38=IntVar();PICAT_38=IntVar();POSITIVE_38=IntVar();NEGATIVE_38=IntVar();HALOGEN_38=IntVar();
	HBD_39=IntVar();HBA_39=IntVar();HYDRO_39=IntVar();PIPIT_39=IntVar();PIPIP_39=IntVar();PICAT_39=IntVar();POSITIVE_39=IntVar();NEGATIVE_39=IntVar();HALOGEN_39=IntVar();
	HBD_40=IntVar();HBA_40=IntVar();HYDRO_40=IntVar();PIPIT_40=IntVar();PIPIP_40=IntVar();PICAT_40=IntVar();POSITIVE_40=IntVar();NEGATIVE_40=IntVar();HALOGEN_40=IntVar();
	HBD_41=IntVar();HBA_41=IntVar();HYDRO_41=IntVar();PIPIT_41=IntVar();PIPIP_41=IntVar();PICAT_41=IntVar();POSITIVE_41=IntVar();NEGATIVE_41=IntVar();HALOGEN_41=IntVar();
	HBD_42=IntVar();HBA_42=IntVar();HYDRO_42=IntVar();PIPIT_42=IntVar();PIPIP_42=IntVar();PICAT_42=IntVar();POSITIVE_42=IntVar();NEGATIVE_42=IntVar();HALOGEN_42=IntVar();
	HBD_43=IntVar();HBA_43=IntVar();HYDRO_43=IntVar();PIPIT_43=IntVar();PIPIP_43=IntVar();PICAT_43=IntVar();POSITIVE_43=IntVar();NEGATIVE_43=IntVar();HALOGEN_43=IntVar();
	HBD_44=IntVar();HBA_44=IntVar();HYDRO_44=IntVar();PIPIT_44=IntVar();PIPIP_44=IntVar();PICAT_44=IntVar();POSITIVE_44=IntVar();NEGATIVE_44=IntVar();HALOGEN_44=IntVar();
	HBD_45=IntVar();HBA_45=IntVar();HYDRO_45=IntVar();PIPIT_45=IntVar();PIPIP_45=IntVar();PICAT_45=IntVar();POSITIVE_45=IntVar();NEGATIVE_45=IntVar();HALOGEN_45=IntVar();
	HBD_46=IntVar();HBA_46=IntVar();HYDRO_46=IntVar();PIPIT_46=IntVar();PIPIP_46=IntVar();PICAT_46=IntVar();POSITIVE_46=IntVar();NEGATIVE_46=IntVar();HALOGEN_46=IntVar();
	HBD_47=IntVar();HBA_47=IntVar();HYDRO_47=IntVar();PIPIT_47=IntVar();PIPIP_47=IntVar();PICAT_47=IntVar();POSITIVE_47=IntVar();NEGATIVE_47=IntVar();HALOGEN_47=IntVar();
	HBD_48=IntVar();HBA_48=IntVar();HYDRO_48=IntVar();PIPIT_48=IntVar();PIPIP_48=IntVar();PICAT_48=IntVar();POSITIVE_48=IntVar();NEGATIVE_48=IntVar();HALOGEN_48=IntVar();
	HBD_49=IntVar();HBA_49=IntVar();HYDRO_49=IntVar();PIPIT_49=IntVar();PIPIP_49=IntVar();PICAT_49=IntVar();POSITIVE_49=IntVar();NEGATIVE_49=IntVar();HALOGEN_49=IntVar();
	HBD_50=IntVar();HBA_50=IntVar();HYDRO_50=IntVar();PIPIT_50=IntVar();PIPIP_50=IntVar();PICAT_50=IntVar();POSITIVE_50=IntVar();NEGATIVE_50=IntVar();HALOGEN_50=IntVar();
	HBD_51=IntVar();HBA_51=IntVar();HYDRO_51=IntVar();PIPIT_51=IntVar();PIPIP_51=IntVar();PICAT_51=IntVar();POSITIVE_51=IntVar();NEGATIVE_51=IntVar();HALOGEN_51=IntVar();
	HBD_52=IntVar();HBA_52=IntVar();HYDRO_52=IntVar();PIPIT_52=IntVar();PIPIP_52=IntVar();PICAT_52=IntVar();POSITIVE_52=IntVar();NEGATIVE_52=IntVar();HALOGEN_52=IntVar();
	HBD_53=IntVar();HBA_53=IntVar();HYDRO_53=IntVar();PIPIT_53=IntVar();PIPIP_53=IntVar();PICAT_53=IntVar();POSITIVE_53=IntVar();NEGATIVE_53=IntVar();HALOGEN_53=IntVar();
	HBD_54=IntVar();HBA_54=IntVar();HYDRO_54=IntVar();PIPIT_54=IntVar();PIPIP_54=IntVar();PICAT_54=IntVar();POSITIVE_54=IntVar();NEGATIVE_54=IntVar();HALOGEN_54=IntVar();
	HBD_55=IntVar();HBA_55=IntVar();HYDRO_55=IntVar();PIPIT_55=IntVar();PIPIP_55=IntVar();PICAT_55=IntVar();POSITIVE_55=IntVar();NEGATIVE_55=IntVar();HALOGEN_55=IntVar();
	HBD_56=IntVar();HBA_56=IntVar();HYDRO_56=IntVar();PIPIT_56=IntVar();PIPIP_56=IntVar();PICAT_56=IntVar();POSITIVE_56=IntVar();NEGATIVE_56=IntVar();HALOGEN_56=IntVar();
	HBD_57=IntVar();HBA_57=IntVar();HYDRO_57=IntVar();PIPIT_57=IntVar();PIPIP_57=IntVar();PICAT_57=IntVar();POSITIVE_57=IntVar();NEGATIVE_57=IntVar();HALOGEN_57=IntVar();
	HBD_58=IntVar();HBA_58=IntVar();HYDRO_58=IntVar();PIPIT_58=IntVar();PIPIP_58=IntVar();PICAT_58=IntVar();POSITIVE_58=IntVar();NEGATIVE_58=IntVar();HALOGEN_58=IntVar();
	HBD_59=IntVar();HBA_59=IntVar();HYDRO_59=IntVar();PIPIT_59=IntVar();PIPIP_59=IntVar();PICAT_59=IntVar();POSITIVE_59=IntVar();NEGATIVE_59=IntVar();HALOGEN_59=IntVar();
	HBD_60=IntVar();HBA_60=IntVar();HYDRO_60=IntVar();PIPIT_60=IntVar();PIPIP_60=IntVar();PICAT_60=IntVar();POSITIVE_60=IntVar();NEGATIVE_60=IntVar();HALOGEN_60=IntVar();
	HBD_61=IntVar();HBA_61=IntVar();HYDRO_61=IntVar();PIPIT_61=IntVar();PIPIP_61=IntVar();PICAT_61=IntVar();POSITIVE_61=IntVar();NEGATIVE_61=IntVar();HALOGEN_61=IntVar();
	HBD_62=IntVar();HBA_62=IntVar();HYDRO_62=IntVar();PIPIT_62=IntVar();PIPIP_62=IntVar();PICAT_62=IntVar();POSITIVE_62=IntVar();NEGATIVE_62=IntVar();HALOGEN_62=IntVar();
	HBD_63=IntVar();HBA_63=IntVar();HYDRO_63=IntVar();PIPIT_63=IntVar();PIPIP_63=IntVar();PICAT_63=IntVar();POSITIVE_63=IntVar();NEGATIVE_63=IntVar();HALOGEN_63=IntVar();
	HBD_64=IntVar();HBA_64=IntVar();HYDRO_64=IntVar();PIPIT_64=IntVar();PIPIP_64=IntVar();PICAT_64=IntVar();POSITIVE_64=IntVar();NEGATIVE_64=IntVar();HALOGEN_64=IntVar();
	HBD_65=IntVar();HBA_65=IntVar();HYDRO_65=IntVar();PIPIT_65=IntVar();PIPIP_65=IntVar();PICAT_65=IntVar();POSITIVE_65=IntVar();NEGATIVE_65=IntVar();HALOGEN_65=IntVar();
	HBD_66=IntVar();HBA_66=IntVar();HYDRO_66=IntVar();PIPIT_66=IntVar();PIPIP_66=IntVar();PICAT_66=IntVar();POSITIVE_66=IntVar();NEGATIVE_66=IntVar();HALOGEN_66=IntVar();
	HBD_67=IntVar();HBA_67=IntVar();HYDRO_67=IntVar();PIPIT_67=IntVar();PIPIP_67=IntVar();PICAT_67=IntVar();POSITIVE_67=IntVar();NEGATIVE_67=IntVar();HALOGEN_67=IntVar();
	HBD_68=IntVar();HBA_68=IntVar();HYDRO_68=IntVar();PIPIT_68=IntVar();PIPIP_68=IntVar();PICAT_68=IntVar();POSITIVE_68=IntVar();NEGATIVE_68=IntVar();HALOGEN_68=IntVar();
	HBD_69=IntVar();HBA_69=IntVar();HYDRO_69=IntVar();PIPIT_69=IntVar();PIPIP_69=IntVar();PICAT_69=IntVar();POSITIVE_69=IntVar();NEGATIVE_69=IntVar();HALOGEN_69=IntVar();
	HBD_70=IntVar();HBA_70=IntVar();HYDRO_70=IntVar();PIPIT_70=IntVar();PIPIP_70=IntVar();PICAT_70=IntVar();POSITIVE_70=IntVar();NEGATIVE_70=IntVar();HALOGEN_70=IntVar();
	HBD_71=IntVar();HBA_71=IntVar();HYDRO_71=IntVar();PIPIT_71=IntVar();PIPIP_71=IntVar();PICAT_71=IntVar();POSITIVE_71=IntVar();NEGATIVE_71=IntVar();HALOGEN_71=IntVar();
	HBD_72=IntVar();HBA_72=IntVar();HYDRO_72=IntVar();PIPIT_72=IntVar();PIPIP_72=IntVar();PICAT_72=IntVar();POSITIVE_72=IntVar();NEGATIVE_72=IntVar();HALOGEN_72=IntVar();
	HBD_73=IntVar();HBA_73=IntVar();HYDRO_73=IntVar();PIPIT_73=IntVar();PIPIP_73=IntVar();PICAT_73=IntVar();POSITIVE_73=IntVar();NEGATIVE_73=IntVar();HALOGEN_73=IntVar();
	HBD_74=IntVar();HBA_74=IntVar();HYDRO_74=IntVar();PIPIT_74=IntVar();PIPIP_74=IntVar();PICAT_74=IntVar();POSITIVE_74=IntVar();NEGATIVE_74=IntVar();HALOGEN_74=IntVar();
	HBD_75=IntVar();HBA_75=IntVar();HYDRO_75=IntVar();PIPIT_75=IntVar();PIPIP_75=IntVar();PICAT_75=IntVar();POSITIVE_75=IntVar();NEGATIVE_75=IntVar();HALOGEN_75=IntVar();
	HBD_76=IntVar();HBA_76=IntVar();HYDRO_76=IntVar();PIPIT_76=IntVar();PIPIP_76=IntVar();PICAT_76=IntVar();POSITIVE_76=IntVar();NEGATIVE_76=IntVar();HALOGEN_76=IntVar();
	HBD_77=IntVar();HBA_77=IntVar();HYDRO_77=IntVar();PIPIT_77=IntVar();PIPIP_77=IntVar();PICAT_77=IntVar();POSITIVE_77=IntVar();NEGATIVE_77=IntVar();HALOGEN_77=IntVar();
	HBD_78=IntVar();HBA_78=IntVar();HYDRO_78=IntVar();PIPIT_78=IntVar();PIPIP_78=IntVar();PICAT_78=IntVar();POSITIVE_78=IntVar();NEGATIVE_78=IntVar();HALOGEN_78=IntVar();
	HBD_79=IntVar();HBA_79=IntVar();HYDRO_79=IntVar();PIPIT_79=IntVar();PIPIP_79=IntVar();PICAT_79=IntVar();POSITIVE_79=IntVar();NEGATIVE_79=IntVar();HALOGEN_79=IntVar();
	HBD_80=IntVar();HBA_80=IntVar();HYDRO_80=IntVar();PIPIT_80=IntVar();PIPIP_80=IntVar();PICAT_80=IntVar();POSITIVE_80=IntVar();NEGATIVE_80=IntVar();HALOGEN_80=IntVar();
	HBD_81=IntVar();HBA_81=IntVar();HYDRO_81=IntVar();PIPIT_81=IntVar();PIPIP_81=IntVar();PICAT_81=IntVar();POSITIVE_81=IntVar();NEGATIVE_81=IntVar();HALOGEN_81=IntVar();
	HBD_82=IntVar();HBA_82=IntVar();HYDRO_82=IntVar();PIPIT_82=IntVar();PIPIP_82=IntVar();PICAT_82=IntVar();POSITIVE_82=IntVar();NEGATIVE_82=IntVar();HALOGEN_82=IntVar();
	HBD_83=IntVar();HBA_83=IntVar();HYDRO_83=IntVar();PIPIT_83=IntVar();PIPIP_83=IntVar();PICAT_83=IntVar();POSITIVE_83=IntVar();NEGATIVE_83=IntVar();HALOGEN_83=IntVar();
	HBD_84=IntVar();HBA_84=IntVar();HYDRO_84=IntVar();PIPIT_84=IntVar();PIPIP_84=IntVar();PICAT_84=IntVar();POSITIVE_84=IntVar();NEGATIVE_84=IntVar();HALOGEN_84=IntVar();
	HBD_85=IntVar();HBA_85=IntVar();HYDRO_85=IntVar();PIPIT_85=IntVar();PIPIP_85=IntVar();PICAT_85=IntVar();POSITIVE_85=IntVar();NEGATIVE_85=IntVar();HALOGEN_85=IntVar();
	#~~~~ INITIALIZATION~~~~~~~~~~~
	def out():
		print((HBD_1.get(),HBD_4.get(),HYDRO_1.get()))
	def total_close():
		top.destroy
		root.destroy
	#~~~ I
	def fun_I():
		top=Toplevel(analysis_scr)
		top.title('I')
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="yellow",text="I",font=("Arial",10,'bold'),width=10,height=9).grid(row=1,column=0,rowspan=3,sticky=W+E+N+S)
		#~~~ 1
		Label(top,bg="white",text="1",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1)
		Checkbutton(top,variable=HBD_1,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_1,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_1,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_1,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_1,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_1,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_1,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_1,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_1,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~ 2
		Label(top,bg="white",text="2",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=2,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_2,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_2,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_2,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_2,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_2,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_2,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_2,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_2,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_2,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=10,sticky=W+E+N+S)
		#~~~ 3
		Label(top,bg="white",text="3",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=3,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_3,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_3,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_3,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_3,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_3,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_3,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_3,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_3,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_3,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=4,column=2,columnspan=8,sticky=W+E+N+S)

	#~~~ g.l~~~~
	def fun_gl():
		top=Toplevel(analysis_scr)
		top.title('g.l')
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="lawngreen",text="g.l",font=("Arial",10,'bold'),width=8,height=18).grid(row=1,column=0,rowspan=6,sticky=W+E+N+S)
		#~~~ 4
		Label(top,bg="white",text="4",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_4,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_4,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_4,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_4,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_4,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_4,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_4,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_4,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_4,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~ 5
		Label(top,bg="white",text="5",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=2,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_5,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_5,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_5,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_5,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_5,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_5,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_5,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_5,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_5,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=10,sticky=W+E+N+S)
		#~~~ 6
		Label(top,bg="white",text="6",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=3,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_6,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_6,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_6,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_6,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_6,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_6,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_6,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_6,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_6,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=10,sticky=W+E+N+S)
		#~~~~~~ 7
		Label(top,bg="white",text="7",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=4,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_7,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_7,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_7,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_7,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_7,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_7,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_7,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_7,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_7,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=10,sticky=W+E+N+S)
		#~~~~~~ 8
		Label(top,bg="white",text="8",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=5,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_8,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_8,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_8,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_8,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_8,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_8,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_8,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_8,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_8,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=10,sticky=W+E+N+S)
		#~~~~~~ 9
		Label(top,bg="white",text="9",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=6,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_9,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_9,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_9,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_9,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_9,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_9,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_9,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_9,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_9,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=7,column=2,columnspan=8,sticky=W+E+N+S)

	#~~ II ~~~~~~~~~
	def fun_II():
		top=Toplevel(analysis_scr)
		top.title('II')
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="yellow",text="II",font=("Arial",10,'bold'),width=10,height=12).grid(row=1,column=0,rowspan=4,sticky=W+E+N+S)
		#~~~ 10
		Label(top,bg="white",text="10",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_10,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_10,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_10,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_10,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_10,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_10,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_10,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_10,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_10,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~ 11
		Label(top,bg="white",text="11",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=2,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_11,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_11,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_11,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_11,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_11,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_11,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_11,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_11,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_11,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=10,sticky=W+E+N+S)
		#~~~ 12
		Label(top,bg="white",text="12",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=3,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_12,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_12,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_12,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_12,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_12,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_12,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_12,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_12,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_12,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=10,sticky=W+E+N+S)
		#~~~~~~ 13
		Label(top,bg="white",text="13",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=4,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_13,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_13,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_13,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_13,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_13,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_13,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_13,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_13,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_13,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=5,column=2,columnspan=8,sticky=W+E+N+S)
	#~~~ III ~~~~~~
	def fun_III():
		top=Toplevel(analysis_scr)
		top.title('III')
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="yellow",text="III",font=("Arial",10,'bold'),width=10,height=18).grid(row=1,column=0,rowspan=6,sticky=W+E+N+S)
		#~~~ 14
		Label(top,bg="white",text="14",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_14,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_14,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_14,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_14,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_14,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_14,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_14,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_14,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_14,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~ 15
		Label(top,bg="white",text="15",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=2,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_15,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_15,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_15,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_15,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_15,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_15,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_15,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_15,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_15,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=10,sticky=W+E+N+S)
		#~~~ 16
		Label(top,bg="white",text="16",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=3,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_16,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_16,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_16,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_16,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_16,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_16,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_16,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_16,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_16,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=10,sticky=W+E+N+S)
		#~~~~~~ 17
		Label(top,bg="white",text="17",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=4,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_17,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_17,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_17,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_17,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_17,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_17,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_17,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_17,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_17,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=10,sticky=W+E+N+S)
		#~~~~~~ 18
		Label(top,bg="white",text="18",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=5,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_18,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_18,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_18,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_18,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_18,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_18,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_18,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_18,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_18,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=10,sticky=W+E+N+S)
		#~~~~~~ 19
		Label(top,bg="white",text="19",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=6,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_19,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_19,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_19,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_19,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_19,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_19,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_19,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_19,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_19,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=7,column=2,columnspan=8,sticky=W+E+N+S)

	#~~~ aC ~~~~~~~~
	def fun_aC():
		top=Toplevel(analysis_scr)
		top.title("aC")
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="red",text="aC",font=("Arial",10,'bold'),width=10,height=33).grid(row=1,column=0,rowspan=11,sticky=W+E+N+S)
		#~~~ 20
		Label(top,bg="white",text="20",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_20,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_20,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_20,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_20,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_20,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_20,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_20,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_20,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_20,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~ 21
		Label(top,bg="white",text="21",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=2,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_21,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_21,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_21,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_21,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_21,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_21,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_21,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_21,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_21,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=10,sticky=W+E+N+S)
		#~~~ 22
		Label(top,bg="white",text="22",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=3,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_22,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_22,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_22,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_22,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_22,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_22,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_22,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_22,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_22,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=10,sticky=W+E+N+S)
		#~~~~~~ 23
		Label(top,bg="white",text="23",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=4,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_23,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_23,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_23,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_23,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_23,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_23,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_23,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_23,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_23,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=10,sticky=W+E+N+S)
		#~~~~~~ 24
		Label(top,bg="white",text="24",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=5,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_24,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_24,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_24,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_24,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_24,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_24,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_24,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_24,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_24,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=10,sticky=W+E+N+S)
		#~~~~~~ 25
		Label(top,bg="white",text="25",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=6,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_25,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_25,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_25,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_25,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_25,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_25,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_25,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_25,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_25,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=10,sticky=W+E+N+S)
		#~~~~~~ 26
		Label(top,bg="white",text="26",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=7,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_26,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_26,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_26,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_26,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_26,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_26,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_26,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_26,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_26,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=10,sticky=W+E+N+S)
		#~~~~~~ 27
		Label(top,bg="white",text="27",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=8,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_27,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=8,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_27,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=8,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_27,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=8,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_27,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=8,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_27,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=8,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_27,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=8,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_27,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=8,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_27,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=8,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_27,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=8,column=10,sticky=W+E+N+S)
		#~~~~~~ 28
		Label(top,bg="white",text="28",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=9,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_28,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=9,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_28,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=9,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_28,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=9,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_28,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=9,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_28,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=9,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_28,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=9,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_28,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=9,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_28,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=9,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_28,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=9,column=10,sticky=W+E+N+S)
		#~~~~~~ 29
		Label(top,bg="white",text="29",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=10,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_29,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=10,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_29,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=10,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_29,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=10,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_29,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=10,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_29,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=10,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_29,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=10,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_29,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=10,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_29,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=10,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_29,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=10,column=10,sticky=W+E+N+S)
		#~~~~~~ 30
		Label(top,bg="white",text="30",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=11,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_30,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=11,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_30,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=11,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_30,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=11,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_30,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=11,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_30,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=11,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_30,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=11,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_30,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=11,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_30,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=11,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_30,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=11,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=12,column=2,columnspan=8,sticky=W+E+N+S)
	#~~~ b.l ~~~~~~~~
	def fun_bl():
		top=Toplevel(analysis_scr)
		top.title("b.l")
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="lawngreen",text="b.l",font=("Arial",10,'bold'),width=10,height=21).grid(row=1,column=0,rowspan=7,sticky=W+E+N+S)
		#~~~ 31
		Label(top,bg="white",text="31",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_31,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_31,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_31,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_31,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_31,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_31,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_31,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_31,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_31,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~ 32
		Label(top,bg="white",text="32",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=2,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_32,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_32,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_32,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_32,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_32,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_32,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_32,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_32,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_32,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=10,sticky=W+E+N+S)
		#~~~ 33
		Label(top,bg="white",text="33",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=3,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_33,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_33,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_33,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_33,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_33,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_33,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_33,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_33,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_33,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=10,sticky=W+E+N+S)
		#~~~~~~ 34
		Label(top,bg="white",text="34",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=4,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_34,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_34,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_34,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_34,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_34,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_34,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_34,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_34,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_34,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=10,sticky=W+E+N+S)
		#~~~~~~ 35
		Label(top,bg="white",text="35",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=5,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_35,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_35,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_35,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_35,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_35,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_35,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_35,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_35,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_35,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=10,sticky=W+E+N+S)
		#~~~~~~ 36
		Label(top,bg="white",text="36",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=6,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_36,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_36,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_36,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_36,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_36,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_36,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_36,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_36,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_36,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=10,sticky=W+E+N+S)
		#~~~~~~ 37
		Label(top,bg="white",text="37",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=7,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_37,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_37,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_37,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_37,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_37,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_37,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_37,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_37,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_37,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=8,column=2,columnspan=8,sticky=W+E+N+S)
	#~~~ IV ~~~~~~~~
	def fun_IV():
		top=Toplevel(analysis_scr)
		top.title("IV")
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="yellow",text="IV",font=("Arial",10,'bold'),width=10,height=12).grid(row=1,column=0,rowspan=4,sticky=W+E+N+S)
		#~~~ 38
		Label(top,bg="white",text="38",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_38,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_38,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_38,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_38,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_38,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_38,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_38,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_38,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_38,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~ 39
		Label(top,bg="white",text="39",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=2,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_39,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_39,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_39,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_39,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_39,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_39,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_39,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_39,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_39,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=10,sticky=W+E+N+S)
		#~~~ 40
		Label(top,bg="white",text="40",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=3,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_40,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_40,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_40,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_40,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_40,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_40,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_40,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_40,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_40,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=10,sticky=W+E+N+S)
		#~~~~~~ 41
		Label(top,bg="white",text="41",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=4,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_41,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_41,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_41,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_41,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_41,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_41,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_41,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_41,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_41,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=5,column=2,columnspan=8,sticky=W+E+N+S)

	#~~~ V ~~~~~~~~
	def fun_V():
		top=Toplevel(analysis_scr)
		top.title("V")
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="yellow",text="V",font=("Arial",10,'bold'),width=10,height=9).grid(row=1,column=0,rowspan=3,sticky=W+E+N+S)
		#~~~ 42
		Label(top,bg="white",text="42",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_42,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_42,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_42,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_42,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_42,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_42,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_42,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_42,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_42,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~ 43
		Label(top,bg="white",text="43",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=2,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_43,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_43,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_43,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_43,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_43,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_43,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_43,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_43,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_43,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=10,sticky=W+E+N+S)
		#~~~ 44
		Label(top,bg="white",text="44",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=3,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_44,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_44,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_44,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_44,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_44,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_44,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_44,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_44,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_44,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=4,column=2,columnspan=8,sticky=W+E+N+S)

	#~~~ GK ~~~~~~~~
	def fun_GK():
		top=Toplevel(analysis_scr)
		top.title("GK")
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="yellow",text="GK",font=("Arial",10,'bold'),width=10,height=3).grid(row=1,column=0,rowspan=1,sticky=W+E+N+S)
		#~~~ 45
		Label(top,bg="white",text="45",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_45,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_45,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_45,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_45,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_45,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_45,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_45,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_45,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_45,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=2,column=2,columnspan=8,sticky=W+E+N+S)
	#~~~ hinge ~~~~~~~~
	def fun_hinge():
		top=Toplevel(analysis_scr)
		top.title("HINGE")
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="purple",fg="white",text="HINGE",font=("Arial",10,'bold'),width=10,height=9).grid(row=1,column=0,rowspan=3,sticky=W+E+N+S)
		#~~~ 46
		Label(top,bg="white",text="46",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_46,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_46,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_46,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_46,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_46,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_46,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_46,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_46,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_46,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~ 47
		Label(top,bg="white",text="47",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=2,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_47,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_47,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_47,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_47,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_47,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_47,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_47,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_47,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_47,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=10,sticky=W+E+N+S)
		#~~~ 48
		Label(top,bg="white",text="48",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=3,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_48,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_48,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_48,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_48,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_48,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_48,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_48,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_48,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_48,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=4,column=2,columnspan=8,sticky=W+E+N+S)

	#~~~ linker ~~~~~~~~
	def fun_linker():
		top=Toplevel(analysis_scr)
		top.title("linker")
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="lightblue1",text="linker",font=("Arial",10,'bold'),width=10,height=12).grid(row=1,column=0,rowspan=4,sticky=W+E+N+S)
		#~~~ 49
		Label(top,bg="white",text="49",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_49,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_49,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_49,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_49,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_49,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_49,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_49,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_49,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_49,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~ 50
		Label(top,bg="white",text="50",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=2,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_50,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_50,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_50,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_50,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_50,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_50,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_50,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_50,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_50,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=10,sticky=W+E+N+S)
		#~~~ 51
		Label(top,bg="white",text="51",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=3,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_51,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_51,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_51,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_51,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_51,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_51,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_51,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_51,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_51,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=10,sticky=W+E+N+S)
		#~~~~~~ 52
		Label(top,bg="white",text="52",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=4,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_52,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_52,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_52,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_52,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_52,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_52,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_52,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_52,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_52,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=5,column=2,columnspan=8,sticky=W+E+N+S)
	#~~~ aD ~~~~~~~~
	def fun_aD():
		top=Toplevel(analysis_scr)
		top.title("aD")
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="red",text="aD",font=("Arial",10,'bold'),width=10,height=21).grid(row=1,column=0,rowspan=7,sticky=W+E+N+S)
		#~~~ 53
		Label(top,bg="white",text="53",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_53,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_53,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_53,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_53,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_53,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_53,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_53,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_53,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_53,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~ 54
		Label(top,bg="white",text="54",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=2,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_54,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_54,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_54,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_54,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_54,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_54,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_54,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_54,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_54,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=10,sticky=W+E+N+S)
		#~~~ 55
		Label(top,bg="white",text="55",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=3,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_55,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_55,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_55,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_55,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_55,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_55,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_55,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_55,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_55,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=10,sticky=W+E+N+S)
		#~~~~~~ 56
		Label(top,bg="white",text="56",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=4,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_56,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_56,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_56,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_56,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_56,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_56,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_56,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_56,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_56,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=10,sticky=W+E+N+S)
		#~~~~~~ 57
		Label(top,bg="white",text="57",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=5,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_57,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_57,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_57,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_57,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_57,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_57,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_57,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_57,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_57,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=10,sticky=W+E+N+S)
		#~~~~~~ 58
		Label(top,bg="white",text="58",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=6,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_58,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_58,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_58,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_58,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_58,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_58,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_58,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_58,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_58,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=10,sticky=W+E+N+S)
		#~~~~~~ 59
		Label(top,bg="white",text="59",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=7,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_59,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_59,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_59,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_59,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_59,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_59,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_59,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_59,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_59,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=8,column=2,columnspan=8,sticky=W+E+N+S)
	#~~~ aE ~~~~~~~~
	def fun_aE():
		top=Toplevel(analysis_scr)
		top.title("aE")
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="red",text="aE",font=("Arial",10,'bold'),width=10,height=15).grid(row=1,column=0,rowspan=5,sticky=W+E+N+S)
		#~~~ 60
		Label(top,bg="white",text="60",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_60,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_60,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_60,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_60,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_60,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_60,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_60,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_60,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_60,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~ 61
		Label(top,bg="white",text="61",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=2,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_61,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_61,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_61,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_61,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_61,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_61,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_61,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_61,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_61,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=10,sticky=W+E+N+S)
		#~~~ 62
		Label(top,bg="white",text="62",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=3,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_62,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_62,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_62,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_62,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_62,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_62,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_62,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_62,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_62,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=10,sticky=W+E+N+S)
		#~~~~~~ 63
		Label(top,bg="white",text="63",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=4,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_63,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_63,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_63,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_63,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_63,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_63,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_63,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_63,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_63,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=10,sticky=W+E+N+S)
		#~~~~~~ 64
		Label(top,bg="white",text="64",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=5,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_64,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_64,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_64,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_64,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_64,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_64,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_64,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_64,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_64,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=6,column=2,columnspan=8,sticky=W+E+N+S)
	#~~~ VI ~~~~~~~~
	def fun_VI():
		top=Toplevel(analysis_scr)
		top.title("VI")
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="yellow",text="VI",font=("Arial",10,'bold'),width=10,height=9).grid(row=1,column=0,rowspan=3,sticky=W+E+N+S)
		#~~~ 65
		Label(top,bg="white",text="65",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_65,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_65,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_65,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_65,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_65,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_65,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_65,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_65,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_65,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~ 66
		Label(top,bg="white",text="66",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=2,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_66,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_66,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_66,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_66,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_66,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_66,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_66,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_66,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_66,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=10,sticky=W+E+N+S)
		#~~~ 67
		Label(top,bg="white",text="67",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=3,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_67,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_67,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_67,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_67,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_67,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_67,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_67,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_67,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_67,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=4,column=2,columnspan=8,sticky=W+E+N+S)
	#~~~ c.l ~~~~~~~~
	def fun_cl():
		top=Toplevel(analysis_scr)
		top.title("c.l")
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="orange",text="c.l",font=("Arial",10,'bold'),width=10,height=24).grid(row=1,column=0,rowspan=8,sticky=W+E+N+S)
		#~~~ 68
		Label(top,bg="white",text="68",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_68,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_68,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_68,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_68,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_68,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_68,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_68,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_68,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_68,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~ 69
		Label(top,bg="white",text="69",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=2,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_69,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_69,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_69,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_69,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_69,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_69,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_69,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_69,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_69,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=10,sticky=W+E+N+S)
		#~~~ 70
		Label(top,bg="white",text="70",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=3,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_70,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_70,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_70,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_70,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_70,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_70,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_70,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_70,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_70,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=10,sticky=W+E+N+S)
		#~~~~~~ 71
		Label(top,bg="white",text="71",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=4,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_71,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_71,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_71,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_71,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_71,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_71,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_71,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_71,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_71,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=10,sticky=W+E+N+S)
		#~~~~~~ 72
		Label(top,bg="white",text="72",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=5,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_72,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_72,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_72,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_72,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_72,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_72,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_72,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_72,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_72,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=5,column=10,sticky=W+E+N+S)
		#~~~~~~ 73
		Label(top,bg="white",text="73",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=6,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_73,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_73,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_73,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_73,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_73,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_73,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_73,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_73,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_73,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=6,column=10,sticky=W+E+N+S)
		#~~~~~~ 74
		Label(top,bg="white",text="74",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=7,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_74,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_74,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_74,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_74,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_74,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_74,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_74,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_74,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_74,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=7,column=10,sticky=W+E+N+S)
		#~~~~~~ 75
		Label(top,bg="white",text="75",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=8,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_75,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=8,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_75,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=8,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_75,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=8,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_75,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=8,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_75,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=8,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_75,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=8,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_75,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=8,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_75,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=8,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_75,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=8,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=9,column=2,columnspan=8,sticky=W+E+N+S)
	#~~~ VII ~~~~~~~~
	def fun_VII():
		top=Toplevel(analysis_scr)
		top.title("VII")
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="yellow",text="VII",font=("Arial",10,'bold'),width=10,height=9).grid(row=1,column=0,rowspan=3,sticky=W+E+N+S)
		#~~~ 76
		Label(top,bg="white",text="76",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_76,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_76,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_76,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_76,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_76,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_76,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_76,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_76,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_76,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~ 77
		Label(top,bg="white",text="77",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=2,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_77,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_77,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_77,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_77,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_77,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_77,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_77,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_77,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_77,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=10,sticky=W+E+N+S)
		#~~~ 78
		Label(top,bg="white",text="78",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=3,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_78,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_78,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_78,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_78,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_78,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_78,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_78,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_78,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_78,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=4,column=2,columnspan=8,sticky=W+E+N+S)
	#~~~ VIII ~~~~~~~~
	def fun_VIII():
		top=Toplevel(analysis_scr)
		top.title("VIII")
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="yellow",text="VIII",font=("Arial",10,'bold'),width=10,height=3).grid(row=1,column=0,rowspan=1,sticky=W+E+N+S)
		#~~~ 79
		Label(top,bg="white",text="79",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_79,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_79,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_79,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_79,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_79,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_79,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_79,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_79,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_79,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=2,column=2,columnspan=8,sticky=W+E+N+S)
	#~~~ xDFG ~~~~~~~~
	def fun_xDFG():
		top=Toplevel(analysis_scr)
		top.title("xDFG")
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="cornflower blue",text="xDFG",font=("Arial",10,'bold'),width=10,height=12).grid(row=1,column=0,rowspan=4,sticky=W+E+N+S)
		#~~~ 80
		Label(top,bg="white",text="80",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_80,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_80,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_80,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_80,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_80,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_80,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_80,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_80,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_80,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~ 81
		Label(top,bg="white",text="81",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=2,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_81,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_81,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_81,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_81,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_81,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_81,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_81,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_81,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_81,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=10,sticky=W+E+N+S)
		#~~~ 82
		Label(top,bg="white",text="82",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=3,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_82,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_82,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_82,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_82,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_82,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_82,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_82,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_82,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_82,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=3,column=10,sticky=W+E+N+S)
		#~~~ 83
		Label(top,bg="white",text="83",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=4,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_83,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_83,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_83,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_83,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_83,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_83,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_83,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_83,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_83,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=4,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=5,column=2,columnspan=8,sticky=W+E+N+S)
	#~~~ a.l ~~~~~~~~
	def fun_al():
		top=Toplevel(analysis_scr)
		top.title("a.l")
		#~~ Header ~~~~
		Label(top,bg="white",text="Empty",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Label(top,bg="white",text="Pocket No.",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=1,sticky=W+E+N+S)
		Label(top,bg="white",text="HBD",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=2,sticky=W+E+N+S)
		Label(top,bg="white",text="HBA",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=3,sticky=W+E+N+S)
		Label(top,bg="white",text="HYDRO",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=4,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_P",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=5,sticky=W+E+N+S)
		Label(top,bg="white",text="PIPI_T",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=6,sticky=W+E+N+S)
		Label(top,bg="white",text="PI-CAT",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=7,sticky=W+E+N+S)
		Label(top,bg="white",text="POSITIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=8,sticky=W+E+N+S)
		Label(top,bg="white",text="NEGATIVE",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=9,sticky=W+E+N+S)
		Label(top,bg="white",text="HALOGEN",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=0,column=10,sticky=W+E+N+S)
		#~~~ Header ~~~
		#~~~ Entries ~~~
		Label(top,bg="cornflower blue",text="a.l",font=("Arial",10,'bold'),width=10,height=6).grid(row=1,column=0,rowspan=2,sticky=W+E+N+S)
		#~~~ 84
		Label(top,bg="white",text="84",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_84,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_84,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_84,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_84,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_84,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_84,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_84,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_84,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_84,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=10,sticky=W+E+N+S)
		#~~~ 85
		Label(top,bg="white",text="85",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=2,column=1,sticky=W+E+N+S)
		Checkbutton(top,variable=HBD_85,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=2,sticky=W+E+N+S)
		Checkbutton(top,variable=HBA_85,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=3,sticky=W+E+N+S)
		Checkbutton(top,variable=HYDRO_85,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=4,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIP_85,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=5,sticky=W+E+N+S)
		Checkbutton(top,variable=PIPIT_85,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=6,sticky=W+E+N+S)
		Checkbutton(top,variable=PICAT_85,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=7,sticky=W+E+N+S)
		Checkbutton(top,variable=POSITIVE_85,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=8,sticky=W+E+N+S)
		Checkbutton(top,variable=NEGATIVE_85,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=9,sticky=W+E+N+S)
		Checkbutton(top,variable=HALOGEN_85,onvalue=1,offvalue=0,bg="white",width=7,height=3,relief=SOLID).grid(row=2,column=10,sticky=W+E+N+S)
		#~~~~ Entries ~~~~
		Button(top, text="Done",font=("Arial",10,'bold'),relief=RAISED,borderwidth=3,width=10,height=3, command=top.destroy).grid(row=3,column=2,columnspan=8,sticky=W+E+N+S)
	def run_analysis_calc():
		global filename
		global filedir
		global Analysiscount
		global analysisworking
		#~~~~ Check for Files and other input ~~~~
		if not filename:
			tkinter.messagebox.showinfo("Warning","Please provide the input file!")
			return
		#~~~~ Check for Files and other input ~~~~
		os.chdir(filedir)
		#~~~ check if any other analysis dir present or not
		analysisdir=os.listdir('.')
		qwerty=[]
		analysiscountcheck="NO"
		for f in analysisdir:
			if re.match("Analysis_",f):
				analysiscountcheck="YES"
		if analysiscountcheck == "YES":
			for f in analysisdir:
				if re.match("Analysis_",f):
					qwerty.append(f.strip('\n'))
			Analysiscount=int(max(qwerty).split('_')[1])+1
		os.mkdir('Analysis_'+str(Analysiscount)) #Analysiscount
		os.chdir('Analysis_'+str(Analysiscount))
		analysisworking=filedir+'/Analysis_'+str(Analysiscount)
		# 1:HBD, 2:HBA, 3:Hydrophobic, 4:PIPI_P, 5:PIPI_T, 6:PICAT, 7:POSITIVE, 8:NEGATIVE, 9:HALOGEN
		INT={}
		for f in range(1,86):
			INT[f]=[]
		if HBD_1.get() == 1:
			INT[1].append(1)
		if HBA_1.get() == 1:
			INT[1].append(2)
		if HYDRO_1.get() == 1:
			INT[1].append(3)
		if PIPIP_1.get() == 1:
			INT[1].append(4)
		if PIPIT_1.get() == 1:
			INT[1].append(5)
		if PICAT_1.get() == 1:
			INT[1].append(6)
		if POSITIVE_1.get() == 1:
			INT[1].append(7)
		if NEGATIVE_1.get() == 1:
			INT[1].append(8)
		if HALOGEN_1.get() == 1:
			INT[1].append(9)
		if HBD_2.get() == 1:
			INT[2].append(1)
		if HBA_2.get() == 1:
			INT[2].append(2)
		if HYDRO_2.get() == 1:
			INT[2].append(3)
		if PIPIP_2.get() == 1:
			INT[2].append(4)
		if PIPIT_2.get() == 1:
			INT[2].append(5)
		if PICAT_2.get() == 1:
			INT[2].append(6)
		if POSITIVE_2.get() == 1:
			INT[2].append(7)
		if NEGATIVE_2.get() == 1:
			INT[2].append(8)
		if HALOGEN_2.get() == 1:
			INT[2].append(9)
		if HBD_3.get() == 1:
			INT[3].append(1)
		if HBA_3.get() == 1:
			INT[3].append(2)
		if HYDRO_3.get() == 1:
			INT[3].append(3)
		if PIPIP_3.get() == 1:
			INT[3].append(4)
		if PIPIT_3.get() == 1:
			INT[3].append(5)
		if PICAT_3.get() == 1:
			INT[3].append(6)
		if POSITIVE_3.get() == 1:
			INT[3].append(7)
		if NEGATIVE_3.get() == 1:
			INT[3].append(8)
		if HALOGEN_3.get() == 1:
			INT[3].append(9)
		if HBD_4.get() == 1:
			INT[4].append(1)
		if HBA_4.get() == 1:
			INT[4].append(2)
		if HYDRO_4.get() == 1:
			INT[4].append(3)
		if PIPIP_4.get() == 1:
			INT[4].append(4)
		if PIPIT_4.get() == 1:
			INT[4].append(5)
		if PICAT_4.get() == 1:
			INT[4].append(6)
		if POSITIVE_4.get() == 1:
			INT[4].append(7)
		if NEGATIVE_4.get() == 1:
			INT[4].append(8)
		if HALOGEN_4.get() == 1:
			INT[4].append(9)
		if HBD_5.get() == 1:
			INT[5].append(1)
		if HBA_5.get() == 1:
			INT[5].append(2)
		if HYDRO_5.get() == 1:
			INT[5].append(3)
		if PIPIP_5.get() == 1:
			INT[5].append(4)
		if PIPIT_5.get() == 1:
			INT[5].append(5)
		if PICAT_5.get() == 1:
			INT[5].append(6)
		if POSITIVE_5.get() == 1:
			INT[5].append(7)
		if NEGATIVE_5.get() == 1:
			INT[5].append(8)
		if HALOGEN_5.get() == 1:
			INT[5].append(9)
		if HBD_6.get() == 1:
			INT[6].append(1)
		if HBA_6.get() == 1:
			INT[6].append(2)
		if HYDRO_6.get() == 1:
			INT[6].append(3)
		if PIPIP_6.get() == 1:
			INT[6].append(4)
		if PIPIT_6.get() == 1:
			INT[6].append(5)
		if PICAT_6.get() == 1:
			INT[6].append(6)
		if POSITIVE_6.get() == 1:
			INT[6].append(7)
		if NEGATIVE_6.get() == 1:
			INT[6].append(8)
		if HALOGEN_6.get() == 1:
			INT[6].append(9)
		if HBD_7.get() == 1:
			INT[7].append(1)
		if HBA_7.get() == 1:
			INT[7].append(2)
		if HYDRO_7.get() == 1:
			INT[7].append(3)
		if PIPIP_7.get() == 1:
			INT[7].append(4)
		if PIPIT_7.get() == 1:
			INT[7].append(5)
		if PICAT_7.get() == 1:
			INT[7].append(6)
		if POSITIVE_7.get() == 1:
			INT[7].append(7)
		if NEGATIVE_7.get() == 1:
			INT[7].append(8)
		if HALOGEN_7.get() == 1:
			INT[7].append(9)
		if HBD_8.get() == 1:
			INT[8].append(1)
		if HBA_8.get() == 1:
			INT[8].append(2)
		if HYDRO_8.get() == 1:
			INT[8].append(3)
		if PIPIP_8.get() == 1:
			INT[8].append(4)
		if PIPIT_8.get() == 1:
			INT[8].append(5)
		if PICAT_8.get() == 1:
			INT[8].append(6)
		if POSITIVE_8.get() == 1:
			INT[8].append(7)
		if NEGATIVE_8.get() == 1:
			INT[8].append(8)
		if HALOGEN_8.get() == 1:
			INT[8].append(9)
		if HBD_9.get() == 1:
			INT[9].append(1)
		if HBA_9.get() == 1:
			INT[9].append(2)
		if HYDRO_9.get() == 1:
			INT[9].append(3)
		if PIPIP_9.get() == 1:
			INT[9].append(4)
		if PIPIT_9.get() == 1:
			INT[9].append(5)
		if PICAT_9.get() == 1:
			INT[9].append(6)
		if POSITIVE_9.get() == 1:
			INT[9].append(7)
		if NEGATIVE_9.get() == 1:
			INT[9].append(8)
		if HALOGEN_9.get() == 1:
			INT[9].append(9)
		if HBD_10.get() == 1:
			INT[10].append(1)
		if HBA_10.get() == 1:
			INT[10].append(2)
		if HYDRO_10.get() == 1:
			INT[10].append(3)
		if PIPIP_10.get() == 1:
			INT[10].append(4)
		if PIPIT_10.get() == 1:
			INT[10].append(5)
		if PICAT_10.get() == 1:
			INT[10].append(6)
		if POSITIVE_10.get() == 1:
			INT[10].append(7)
		if NEGATIVE_10.get() == 1:
			INT[10].append(8)
		if HALOGEN_10.get() == 1:
			INT[10].append(9)
		if HBD_11.get() == 1:
			INT[11].append(1)
		if HBA_11.get() == 1:
			INT[11].append(2)
		if HYDRO_11.get() == 1:
			INT[11].append(3)
		if PIPIP_11.get() == 1:
			INT[11].append(4)
		if PIPIT_11.get() == 1:
			INT[11].append(5)
		if PICAT_11.get() == 1:
			INT[11].append(6)
		if POSITIVE_11.get() == 1:
			INT[11].append(7)
		if NEGATIVE_11.get() == 1:
			INT[11].append(8)
		if HALOGEN_11.get() == 1:
			INT[11].append(9)
		if HBD_12.get() == 1:
			INT[12].append(1)
		if HBA_12.get() == 1:
			INT[12].append(2)
		if HYDRO_12.get() == 1:
			INT[12].append(3)
		if PIPIP_12.get() == 1:
			INT[12].append(4)
		if PIPIT_12.get() == 1:
			INT[12].append(5)
		if PICAT_12.get() == 1:
			INT[12].append(6)
		if POSITIVE_12.get() == 1:
			INT[12].append(7)
		if NEGATIVE_12.get() == 1:
			INT[12].append(8)
		if HALOGEN_12.get() == 1:
			INT[12].append(9)
		if HBD_13.get() == 1:
			INT[13].append(1)
		if HBA_13.get() == 1:
			INT[13].append(2)
		if HYDRO_13.get() == 1:
			INT[13].append(3)
		if PIPIP_13.get() == 1:
			INT[13].append(4)
		if PIPIT_13.get() == 1:
			INT[13].append(5)
		if PICAT_13.get() == 1:
			INT[13].append(6)
		if POSITIVE_13.get() == 1:
			INT[13].append(7)
		if NEGATIVE_13.get() == 1:
			INT[13].append(8)
		if HALOGEN_13.get() == 1:
			INT[13].append(9)
		if HBD_14.get() == 1:
			INT[14].append(1)
		if HBA_14.get() == 1:
			INT[14].append(2)
		if HYDRO_14.get() == 1:
			INT[14].append(3)
		if PIPIP_14.get() == 1:
			INT[14].append(4)
		if PIPIT_14.get() == 1:
			INT[14].append(5)
		if PICAT_14.get() == 1:
			INT[14].append(6)
		if POSITIVE_14.get() == 1:
			INT[14].append(7)
		if NEGATIVE_14.get() == 1:
			INT[14].append(8)
		if HALOGEN_14.get() == 1:
			INT[14].append(9)
		if HBD_15.get() == 1:
			INT[15].append(1)
		if HBA_15.get() == 1:
			INT[15].append(2)
		if HYDRO_15.get() == 1:
			INT[15].append(3)
		if PIPIP_15.get() == 1:
			INT[15].append(4)
		if PIPIT_15.get() == 1:
			INT[15].append(5)
		if PICAT_15.get() == 1:
			INT[15].append(6)
		if POSITIVE_15.get() == 1:
			INT[15].append(7)
		if NEGATIVE_15.get() == 1:
			INT[15].append(8)
		if HALOGEN_15.get() == 1:
			INT[15].append(9)
		if HBD_16.get() == 1:
			INT[16].append(1)
		if HBA_16.get() == 1:
			INT[16].append(2)
		if HYDRO_16.get() == 1:
			INT[16].append(3)
		if PIPIP_16.get() == 1:
			INT[16].append(4)
		if PIPIT_16.get() == 1:
			INT[16].append(5)
		if PICAT_16.get() == 1:
			INT[16].append(6)
		if POSITIVE_16.get() == 1:
			INT[16].append(7)
		if NEGATIVE_16.get() == 1:
			INT[16].append(8)
		if HALOGEN_16.get() == 1:
			INT[16].append(9)
		if HBD_17.get() == 1:
			INT[17].append(1)
		if HBA_17.get() == 1:
			INT[17].append(2)
		if HYDRO_17.get() == 1:
			INT[17].append(3)
		if PIPIP_17.get() == 1:
			INT[17].append(4)
		if PIPIT_17.get() == 1:
			INT[17].append(5)
		if PICAT_17.get() == 1:
			INT[17].append(6)
		if POSITIVE_17.get() == 1:
			INT[17].append(7)
		if NEGATIVE_17.get() == 1:
			INT[17].append(8)
		if HALOGEN_17.get() == 1:
			INT[17].append(9)
		if HBD_18.get() == 1:
			INT[18].append(1)
		if HBA_18.get() == 1:
			INT[18].append(2)
		if HYDRO_18.get() == 1:
			INT[18].append(3)
		if PIPIP_18.get() == 1:
			INT[18].append(4)
		if PIPIT_18.get() == 1:
			INT[18].append(5)
		if PICAT_18.get() == 1:
			INT[18].append(6)
		if POSITIVE_18.get() == 1:
			INT[18].append(7)
		if NEGATIVE_18.get() == 1:
			INT[18].append(8)
		if HALOGEN_18.get() == 1:
			INT[18].append(9)
		if HBD_19.get() == 1:
			INT[19].append(1)
		if HBA_19.get() == 1:
			INT[19].append(2)
		if HYDRO_19.get() == 1:
			INT[19].append(3)
		if PIPIP_19.get() == 1:
			INT[19].append(4)
		if PIPIT_19.get() == 1:
			INT[19].append(5)
		if PICAT_19.get() == 1:
			INT[19].append(6)
		if POSITIVE_19.get() == 1:
			INT[19].append(7)
		if NEGATIVE_19.get() == 1:
			INT[19].append(8)
		if HALOGEN_19.get() == 1:
			INT[19].append(9)
		if HBD_20.get() == 1:
			INT[20].append(1)
		if HBA_20.get() == 1:
			INT[20].append(2)
		if HYDRO_20.get() == 1:
			INT[20].append(3)
		if PIPIP_20.get() == 1:
			INT[20].append(4)
		if PIPIT_20.get() == 1:
			INT[20].append(5)
		if PICAT_20.get() == 1:
			INT[20].append(6)
		if POSITIVE_20.get() == 1:
			INT[20].append(7)
		if NEGATIVE_20.get() == 1:
			INT[20].append(8)
		if HALOGEN_20.get() == 1:
			INT[20].append(9)
		if HBD_21.get() == 1:
			INT[21].append(1)
		if HBA_21.get() == 1:
			INT[21].append(2)
		if HYDRO_21.get() == 1:
			INT[21].append(3)
		if PIPIP_21.get() == 1:
			INT[21].append(4)
		if PIPIT_21.get() == 1:
			INT[21].append(5)
		if PICAT_21.get() == 1:
			INT[21].append(6)
		if POSITIVE_21.get() == 1:
			INT[21].append(7)
		if NEGATIVE_21.get() == 1:
			INT[21].append(8)
		if HALOGEN_21.get() == 1:
			INT[21].append(9)
		if HBD_22.get() == 1:
			INT[22].append(1)
		if HBA_22.get() == 1:
			INT[22].append(2)
		if HYDRO_22.get() == 1:
			INT[22].append(3)
		if PIPIP_22.get() == 1:
			INT[22].append(4)
		if PIPIT_22.get() == 1:
			INT[22].append(5)
		if PICAT_22.get() == 1:
			INT[22].append(6)
		if POSITIVE_22.get() == 1:
			INT[22].append(7)
		if NEGATIVE_22.get() == 1:
			INT[22].append(8)
		if HALOGEN_22.get() == 1:
			INT[22].append(9)
		if HBD_23.get() == 1:
			INT[23].append(1)
		if HBA_23.get() == 1:
			INT[23].append(2)
		if HYDRO_23.get() == 1:
			INT[23].append(3)
		if PIPIP_23.get() == 1:
			INT[23].append(4)
		if PIPIT_23.get() == 1:
			INT[23].append(5)
		if PICAT_23.get() == 1:
			INT[23].append(6)
		if POSITIVE_23.get() == 1:
			INT[23].append(7)
		if NEGATIVE_23.get() == 1:
			INT[23].append(8)
		if HALOGEN_23.get() == 1:
			INT[23].append(9)
		if HBD_24.get() == 1:
			INT[24].append(1)
		if HBA_24.get() == 1:
			INT[24].append(2)
		if HYDRO_24.get() == 1:
			INT[24].append(3)
		if PIPIP_24.get() == 1:
			INT[24].append(4)
		if PIPIT_24.get() == 1:
			INT[24].append(5)
		if PICAT_24.get() == 1:
			INT[24].append(6)
		if POSITIVE_24.get() == 1:
			INT[24].append(7)
		if NEGATIVE_24.get() == 1:
			INT[24].append(8)
		if HALOGEN_24.get() == 1:
			INT[24].append(9)
		if HBD_25.get() == 1:
			INT[25].append(1)
		if HBA_25.get() == 1:
			INT[25].append(2)
		if HYDRO_25.get() == 1:
			INT[25].append(3)
		if PIPIP_25.get() == 1:
			INT[25].append(4)
		if PIPIT_25.get() == 1:
			INT[25].append(5)
		if PICAT_25.get() == 1:
			INT[25].append(6)
		if POSITIVE_25.get() == 1:
			INT[25].append(7)
		if NEGATIVE_25.get() == 1:
			INT[25].append(8)
		if HALOGEN_25.get() == 1:
			INT[25].append(9)
		if HBD_26.get() == 1:
			INT[26].append(1)
		if HBA_26.get() == 1:
			INT[26].append(2)
		if HYDRO_26.get() == 1:
			INT[26].append(3)
		if PIPIP_26.get() == 1:
			INT[26].append(4)
		if PIPIT_26.get() == 1:
			INT[26].append(5)
		if PICAT_26.get() == 1:
			INT[26].append(6)
		if POSITIVE_26.get() == 1:
			INT[26].append(7)
		if NEGATIVE_26.get() == 1:
			INT[26].append(8)
		if HALOGEN_26.get() == 1:
			INT[26].append(9)
		if HBD_27.get() == 1:
			INT[27].append(1)
		if HBA_27.get() == 1:
			INT[27].append(2)
		if HYDRO_27.get() == 1:
			INT[27].append(3)
		if PIPIP_27.get() == 1:
			INT[27].append(4)
		if PIPIT_27.get() == 1:
			INT[27].append(5)
		if PICAT_27.get() == 1:
			INT[27].append(6)
		if POSITIVE_27.get() == 1:
			INT[27].append(7)
		if NEGATIVE_27.get() == 1:
			INT[27].append(8)
		if HALOGEN_27.get() == 1:
			INT[27].append(9)
		if HBD_28.get() == 1:
			INT[28].append(1)
		if HBA_28.get() == 1:
			INT[28].append(2)
		if HYDRO_28.get() == 1:
			INT[28].append(3)
		if PIPIP_28.get() == 1:
			INT[28].append(4)
		if PIPIT_28.get() == 1:
			INT[28].append(5)
		if PICAT_28.get() == 1:
			INT[28].append(6)
		if POSITIVE_28.get() == 1:
			INT[28].append(7)
		if NEGATIVE_28.get() == 1:
			INT[28].append(8)
		if HALOGEN_28.get() == 1:
			INT[28].append(9)
		if HBD_29.get() == 1:
			INT[29].append(1)
		if HBA_29.get() == 1:
			INT[29].append(2)
		if HYDRO_29.get() == 1:
			INT[29].append(3)
		if PIPIP_29.get() == 1:
			INT[29].append(4)
		if PIPIT_29.get() == 1:
			INT[29].append(5)
		if PICAT_29.get() == 1:
			INT[29].append(6)
		if POSITIVE_29.get() == 1:
			INT[29].append(7)
		if NEGATIVE_29.get() == 1:
			INT[29].append(8)
		if HALOGEN_29.get() == 1:
			INT[29].append(9)
		if HBD_30.get() == 1:
			INT[30].append(1)
		if HBA_30.get() == 1:
			INT[30].append(2)
		if HYDRO_30.get() == 1:
			INT[30].append(3)
		if PIPIP_30.get() == 1:
			INT[30].append(4)
		if PIPIT_30.get() == 1:
			INT[30].append(5)
		if PICAT_30.get() == 1:
			INT[30].append(6)
		if POSITIVE_30.get() == 1:
			INT[30].append(7)
		if NEGATIVE_30.get() == 1:
			INT[30].append(8)
		if HALOGEN_30.get() == 1:
			INT[30].append(9)
		if HBD_31.get() == 1:
			INT[31].append(1)
		if HBA_31.get() == 1:
			INT[31].append(2)
		if HYDRO_31.get() == 1:
			INT[31].append(3)
		if PIPIP_31.get() == 1:
			INT[31].append(4)
		if PIPIT_31.get() == 1:
			INT[31].append(5)
		if PICAT_31.get() == 1:
			INT[31].append(6)
		if POSITIVE_31.get() == 1:
			INT[31].append(7)
		if NEGATIVE_31.get() == 1:
			INT[31].append(8)
		if HALOGEN_31.get() == 1:
			INT[31].append(9)
		if HBD_32.get() == 1:
			INT[32].append(1)
		if HBA_32.get() == 1:
			INT[32].append(2)
		if HYDRO_32.get() == 1:
			INT[32].append(3)
		if PIPIP_32.get() == 1:
			INT[32].append(4)
		if PIPIT_32.get() == 1:
			INT[32].append(5)
		if PICAT_32.get() == 1:
			INT[32].append(6)
		if POSITIVE_32.get() == 1:
			INT[32].append(7)
		if NEGATIVE_32.get() == 1:
			INT[32].append(8)
		if HALOGEN_32.get() == 1:
			INT[32].append(9)
		if HBD_33.get() == 1:
			INT[33].append(1)
		if HBA_33.get() == 1:
			INT[33].append(2)
		if HYDRO_33.get() == 1:
			INT[33].append(3)
		if PIPIP_33.get() == 1:
			INT[33].append(4)
		if PIPIT_33.get() == 1:
			INT[33].append(5)
		if PICAT_33.get() == 1:
			INT[33].append(6)
		if POSITIVE_33.get() == 1:
			INT[33].append(7)
		if NEGATIVE_33.get() == 1:
			INT[33].append(8)
		if HALOGEN_33.get() == 1:
			INT[33].append(9)
		if HBD_34.get() == 1:
			INT[34].append(1)
		if HBA_34.get() == 1:
			INT[34].append(2)
		if HYDRO_34.get() == 1:
			INT[34].append(3)
		if PIPIP_34.get() == 1:
			INT[34].append(4)
		if PIPIT_34.get() == 1:
			INT[34].append(5)
		if PICAT_34.get() == 1:
			INT[34].append(6)
		if POSITIVE_34.get() == 1:
			INT[34].append(7)
		if NEGATIVE_34.get() == 1:
			INT[34].append(8)
		if HALOGEN_34.get() == 1:
			INT[34].append(9)
		if HBD_35.get() == 1:
			INT[35].append(1)
		if HBA_35.get() == 1:
			INT[35].append(2)
		if HYDRO_35.get() == 1:
			INT[35].append(3)
		if PIPIP_35.get() == 1:
			INT[35].append(4)
		if PIPIT_35.get() == 1:
			INT[35].append(5)
		if PICAT_35.get() == 1:
			INT[35].append(6)
		if POSITIVE_35.get() == 1:
			INT[35].append(7)
		if NEGATIVE_35.get() == 1:
			INT[35].append(8)
		if HALOGEN_35.get() == 1:
			INT[35].append(9)
		if HBD_36.get() == 1:
			INT[36].append(1)
		if HBA_36.get() == 1:
			INT[36].append(2)
		if HYDRO_36.get() == 1:
			INT[36].append(3)
		if PIPIP_36.get() == 1:
			INT[36].append(4)
		if PIPIT_36.get() == 1:
			INT[36].append(5)
		if PICAT_36.get() == 1:
			INT[36].append(6)
		if POSITIVE_36.get() == 1:
			INT[36].append(7)
		if NEGATIVE_36.get() == 1:
			INT[36].append(8)
		if HALOGEN_36.get() == 1:
			INT[36].append(9)
		if HBD_37.get() == 1:
			INT[37].append(1)
		if HBA_37.get() == 1:
			INT[37].append(2)
		if HYDRO_37.get() == 1:
			INT[37].append(3)
		if PIPIP_37.get() == 1:
			INT[37].append(4)
		if PIPIT_37.get() == 1:
			INT[37].append(5)
		if PICAT_37.get() == 1:
			INT[37].append(6)
		if POSITIVE_37.get() == 1:
			INT[37].append(7)
		if NEGATIVE_37.get() == 1:
			INT[37].append(8)
		if HALOGEN_37.get() == 1:
			INT[37].append(9)
		if HBD_38.get() == 1:
			INT[38].append(1)
		if HBA_38.get() == 1:
			INT[38].append(2)
		if HYDRO_38.get() == 1:
			INT[38].append(3)
		if PIPIP_38.get() == 1:
			INT[38].append(4)
		if PIPIT_38.get() == 1:
			INT[38].append(5)
		if PICAT_38.get() == 1:
			INT[38].append(6)
		if POSITIVE_38.get() == 1:
			INT[38].append(7)
		if NEGATIVE_38.get() == 1:
			INT[38].append(8)
		if HALOGEN_38.get() == 1:
			INT[38].append(9)
		if HBD_39.get() == 1:
			INT[39].append(1)
		if HBA_39.get() == 1:
			INT[39].append(2)
		if HYDRO_39.get() == 1:
			INT[39].append(3)
		if PIPIP_39.get() == 1:
			INT[39].append(4)
		if PIPIT_39.get() == 1:
			INT[39].append(5)
		if PICAT_39.get() == 1:
			INT[39].append(6)
		if POSITIVE_39.get() == 1:
			INT[39].append(7)
		if NEGATIVE_39.get() == 1:
			INT[39].append(8)
		if HALOGEN_39.get() == 1:
			INT[39].append(9)
		if HBD_40.get() == 1:
			INT[40].append(1)
		if HBA_40.get() == 1:
			INT[40].append(2)
		if HYDRO_40.get() == 1:
			INT[40].append(3)
		if PIPIP_40.get() == 1:
			INT[40].append(4)
		if PIPIT_40.get() == 1:
			INT[40].append(5)
		if PICAT_40.get() == 1:
			INT[40].append(6)
		if POSITIVE_40.get() == 1:
			INT[40].append(7)
		if NEGATIVE_40.get() == 1:
			INT[40].append(8)
		if HALOGEN_40.get() == 1:
			INT[40].append(9)
		if HBD_41.get() == 1:
			INT[41].append(1)
		if HBA_41.get() == 1:
			INT[41].append(2)
		if HYDRO_41.get() == 1:
			INT[41].append(3)
		if PIPIP_41.get() == 1:
			INT[41].append(4)
		if PIPIT_41.get() == 1:
			INT[41].append(5)
		if PICAT_41.get() == 1:
			INT[41].append(6)
		if POSITIVE_41.get() == 1:
			INT[41].append(7)
		if NEGATIVE_41.get() == 1:
			INT[41].append(8)
		if HALOGEN_41.get() == 1:
			INT[41].append(9)
		if HBD_42.get() == 1:
			INT[42].append(1)
		if HBA_42.get() == 1:
			INT[42].append(2)
		if HYDRO_42.get() == 1:
			INT[42].append(3)
		if PIPIP_42.get() == 1:
			INT[42].append(4)
		if PIPIT_42.get() == 1:
			INT[42].append(5)
		if PICAT_42.get() == 1:
			INT[42].append(6)
		if POSITIVE_42.get() == 1:
			INT[42].append(7)
		if NEGATIVE_42.get() == 1:
			INT[42].append(8)
		if HALOGEN_42.get() == 1:
			INT[42].append(9)
		if HBD_43.get() == 1:
			INT[43].append(1)
		if HBA_43.get() == 1:
			INT[43].append(2)
		if HYDRO_43.get() == 1:
			INT[43].append(3)
		if PIPIP_43.get() == 1:
			INT[43].append(4)
		if PIPIT_43.get() == 1:
			INT[43].append(5)
		if PICAT_43.get() == 1:
			INT[43].append(6)
		if POSITIVE_43.get() == 1:
			INT[43].append(7)
		if NEGATIVE_43.get() == 1:
			INT[43].append(8)
		if HALOGEN_43.get() == 1:
			INT[43].append(9)
		if HBD_44.get() == 1:
			INT[44].append(1)
		if HBA_44.get() == 1:
			INT[44].append(2)
		if HYDRO_44.get() == 1:
			INT[44].append(3)
		if PIPIP_44.get() == 1:
			INT[44].append(4)
		if PIPIT_44.get() == 1:
			INT[44].append(5)
		if PICAT_44.get() == 1:
			INT[44].append(6)
		if POSITIVE_44.get() == 1:
			INT[44].append(7)
		if NEGATIVE_44.get() == 1:
			INT[44].append(8)
		if HALOGEN_44.get() == 1:
			INT[44].append(9)
		if HBD_45.get() == 1:
			INT[45].append(1)
		if HBA_45.get() == 1:
			INT[45].append(2)
		if HYDRO_45.get() == 1:
			INT[45].append(3)
		if PIPIP_45.get() == 1:
			INT[45].append(4)
		if PIPIT_45.get() == 1:
			INT[45].append(5)
		if PICAT_45.get() == 1:
			INT[45].append(6)
		if POSITIVE_45.get() == 1:
			INT[45].append(7)
		if NEGATIVE_45.get() == 1:
			INT[45].append(8)
		if HALOGEN_45.get() == 1:
			INT[45].append(9)
		if HBD_46.get() == 1:
			INT[46].append(1)
		if HBA_46.get() == 1:
			INT[46].append(2)
		if HYDRO_46.get() == 1:
			INT[46].append(3)
		if PIPIP_46.get() == 1:
			INT[46].append(4)
		if PIPIT_46.get() == 1:
			INT[46].append(5)
		if PICAT_46.get() == 1:
			INT[46].append(6)
		if POSITIVE_46.get() == 1:
			INT[46].append(7)
		if NEGATIVE_46.get() == 1:
			INT[46].append(8)
		if HALOGEN_46.get() == 1:
			INT[46].append(9)
		if HBD_47.get() == 1:
			INT[47].append(1)
		if HBA_47.get() == 1:
			INT[47].append(2)
		if HYDRO_47.get() == 1:
			INT[47].append(3)
		if PIPIP_47.get() == 1:
			INT[47].append(4)
		if PIPIT_47.get() == 1:
			INT[47].append(5)
		if PICAT_47.get() == 1:
			INT[47].append(6)
		if POSITIVE_47.get() == 1:
			INT[47].append(7)
		if NEGATIVE_47.get() == 1:
			INT[47].append(8)
		if HALOGEN_47.get() == 1:
			INT[47].append(9)
		if HBD_48.get() == 1:
			INT[48].append(1)
		if HBA_48.get() == 1:
			INT[48].append(2)
		if HYDRO_48.get() == 1:
			INT[48].append(3)
		if PIPIP_48.get() == 1:
			INT[48].append(4)
		if PIPIT_48.get() == 1:
			INT[48].append(5)
		if PICAT_48.get() == 1:
			INT[48].append(6)
		if POSITIVE_48.get() == 1:
			INT[48].append(7)
		if NEGATIVE_48.get() == 1:
			INT[48].append(8)
		if HALOGEN_48.get() == 1:
			INT[48].append(9)
		if HBD_49.get() == 1:
			INT[49].append(1)
		if HBA_49.get() == 1:
			INT[49].append(2)
		if HYDRO_49.get() == 1:
			INT[49].append(3)
		if PIPIP_49.get() == 1:
			INT[49].append(4)
		if PIPIT_49.get() == 1:
			INT[49].append(5)
		if PICAT_49.get() == 1:
			INT[49].append(6)
		if POSITIVE_49.get() == 1:
			INT[49].append(7)
		if NEGATIVE_49.get() == 1:
			INT[49].append(8)
		if HALOGEN_49.get() == 1:
			INT[49].append(9)
		if HBD_50.get() == 1:
			INT[50].append(1)
		if HBA_50.get() == 1:
			INT[50].append(2)
		if HYDRO_50.get() == 1:
			INT[50].append(3)
		if PIPIP_50.get() == 1:
			INT[50].append(4)
		if PIPIT_50.get() == 1:
			INT[50].append(5)
		if PICAT_50.get() == 1:
			INT[50].append(6)
		if POSITIVE_50.get() == 1:
			INT[50].append(7)
		if NEGATIVE_50.get() == 1:
			INT[50].append(8)
		if HALOGEN_50.get() == 1:
			INT[50].append(9)
		if HBD_51.get() == 1:
			INT[51].append(1)
		if HBA_51.get() == 1:
			INT[51].append(2)
		if HYDRO_51.get() == 1:
			INT[51].append(3)
		if PIPIP_51.get() == 1:
			INT[51].append(4)
		if PIPIT_51.get() == 1:
			INT[51].append(5)
		if PICAT_51.get() == 1:
			INT[51].append(6)
		if POSITIVE_51.get() == 1:
			INT[51].append(7)
		if NEGATIVE_51.get() == 1:
			INT[51].append(8)
		if HALOGEN_51.get() == 1:
			INT[51].append(9)
		if HBD_52.get() == 1:
			INT[52].append(1)
		if HBA_52.get() == 1:
			INT[52].append(2)
		if HYDRO_52.get() == 1:
			INT[52].append(3)
		if PIPIP_52.get() == 1:
			INT[52].append(4)
		if PIPIT_52.get() == 1:
			INT[52].append(5)
		if PICAT_52.get() == 1:
			INT[52].append(6)
		if POSITIVE_52.get() == 1:
			INT[52].append(7)
		if NEGATIVE_52.get() == 1:
			INT[52].append(8)
		if HALOGEN_52.get() == 1:
			INT[52].append(9)
		if HBD_53.get() == 1:
			INT[53].append(1)
		if HBA_53.get() == 1:
			INT[53].append(2)
		if HYDRO_53.get() == 1:
			INT[53].append(3)
		if PIPIP_53.get() == 1:
			INT[53].append(4)
		if PIPIT_53.get() == 1:
			INT[53].append(5)
		if PICAT_53.get() == 1:
			INT[53].append(6)
		if POSITIVE_53.get() == 1:
			INT[53].append(7)
		if NEGATIVE_53.get() == 1:
			INT[53].append(8)
		if HALOGEN_53.get() == 1:
			INT[53].append(9)
		if HBD_54.get() == 1:
			INT[54].append(1)
		if HBA_54.get() == 1:
			INT[54].append(2)
		if HYDRO_54.get() == 1:
			INT[54].append(3)
		if PIPIP_54.get() == 1:
			INT[54].append(4)
		if PIPIT_54.get() == 1:
			INT[54].append(5)
		if PICAT_54.get() == 1:
			INT[54].append(6)
		if POSITIVE_54.get() == 1:
			INT[54].append(7)
		if NEGATIVE_54.get() == 1:
			INT[54].append(8)
		if HALOGEN_54.get() == 1:
			INT[54].append(9)
		if HBD_55.get() == 1:
			INT[55].append(1)
		if HBA_55.get() == 1:
			INT[55].append(2)
		if HYDRO_55.get() == 1:
			INT[55].append(3)
		if PIPIP_55.get() == 1:
			INT[55].append(4)
		if PIPIT_55.get() == 1:
			INT[55].append(5)
		if PICAT_55.get() == 1:
			INT[55].append(6)
		if POSITIVE_55.get() == 1:
			INT[55].append(7)
		if NEGATIVE_55.get() == 1:
			INT[55].append(8)
		if HALOGEN_55.get() == 1:
			INT[55].append(9)
		if HBD_56.get() == 1:
			INT[56].append(1)
		if HBA_56.get() == 1:
			INT[56].append(2)
		if HYDRO_56.get() == 1:
			INT[56].append(3)
		if PIPIP_56.get() == 1:
			INT[56].append(4)
		if PIPIT_56.get() == 1:
			INT[56].append(5)
		if PICAT_56.get() == 1:
			INT[56].append(6)
		if POSITIVE_56.get() == 1:
			INT[56].append(7)
		if NEGATIVE_56.get() == 1:
			INT[56].append(8)
		if HALOGEN_56.get() == 1:
			INT[56].append(9)
		if HBD_57.get() == 1:
			INT[57].append(1)
		if HBA_57.get() == 1:
			INT[57].append(2)
		if HYDRO_57.get() == 1:
			INT[57].append(3)
		if PIPIP_57.get() == 1:
			INT[57].append(4)
		if PIPIT_57.get() == 1:
			INT[57].append(5)
		if PICAT_57.get() == 1:
			INT[57].append(6)
		if POSITIVE_57.get() == 1:
			INT[57].append(7)
		if NEGATIVE_57.get() == 1:
			INT[57].append(8)
		if HALOGEN_57.get() == 1:
			INT[57].append(9)
		if HBD_58.get() == 1:
			INT[58].append(1)
		if HBA_58.get() == 1:
			INT[58].append(2)
		if HYDRO_58.get() == 1:
			INT[58].append(3)
		if PIPIP_58.get() == 1:
			INT[58].append(4)
		if PIPIT_58.get() == 1:
			INT[58].append(5)
		if PICAT_58.get() == 1:
			INT[58].append(6)
		if POSITIVE_58.get() == 1:
			INT[58].append(7)
		if NEGATIVE_58.get() == 1:
			INT[58].append(8)
		if HALOGEN_58.get() == 1:
			INT[58].append(9)
		if HBD_59.get() == 1:
			INT[59].append(1)
		if HBA_59.get() == 1:
			INT[59].append(2)
		if HYDRO_59.get() == 1:
			INT[59].append(3)
		if PIPIP_59.get() == 1:
			INT[59].append(4)
		if PIPIT_59.get() == 1:
			INT[59].append(5)
		if PICAT_59.get() == 1:
			INT[59].append(6)
		if POSITIVE_59.get() == 1:
			INT[59].append(7)
		if NEGATIVE_59.get() == 1:
			INT[59].append(8)
		if HALOGEN_59.get() == 1:
			INT[59].append(9)
		if HBD_60.get() == 1:
			INT[60].append(1)
		if HBA_60.get() == 1:
			INT[60].append(2)
		if HYDRO_60.get() == 1:
			INT[60].append(3)
		if PIPIP_60.get() == 1:
			INT[60].append(4)
		if PIPIT_60.get() == 1:
			INT[60].append(5)
		if PICAT_60.get() == 1:
			INT[60].append(6)
		if POSITIVE_60.get() == 1:
			INT[60].append(7)
		if NEGATIVE_60.get() == 1:
			INT[60].append(8)
		if HALOGEN_60.get() == 1:
			INT[60].append(9)
		if HBD_61.get() == 1:
			INT[61].append(1)
		if HBA_61.get() == 1:
			INT[61].append(2)
		if HYDRO_61.get() == 1:
			INT[61].append(3)
		if PIPIP_61.get() == 1:
			INT[61].append(4)
		if PIPIT_61.get() == 1:
			INT[61].append(5)
		if PICAT_61.get() == 1:
			INT[61].append(6)
		if POSITIVE_61.get() == 1:
			INT[61].append(7)
		if NEGATIVE_61.get() == 1:
			INT[61].append(8)
		if HALOGEN_61.get() == 1:
			INT[61].append(9)
		if HBD_62.get() == 1:
			INT[62].append(1)
		if HBA_62.get() == 1:
			INT[62].append(2)
		if HYDRO_62.get() == 1:
			INT[62].append(3)
		if PIPIP_62.get() == 1:
			INT[62].append(4)
		if PIPIT_62.get() == 1:
			INT[62].append(5)
		if PICAT_62.get() == 1:
			INT[62].append(6)
		if POSITIVE_62.get() == 1:
			INT[62].append(7)
		if NEGATIVE_62.get() == 1:
			INT[62].append(8)
		if HALOGEN_62.get() == 1:
			INT[62].append(9)
		if HBD_63.get() == 1:
			INT[63].append(1)
		if HBA_63.get() == 1:
			INT[63].append(2)
		if HYDRO_63.get() == 1:
			INT[63].append(3)
		if PIPIP_63.get() == 1:
			INT[63].append(4)
		if PIPIT_63.get() == 1:
			INT[63].append(5)
		if PICAT_63.get() == 1:
			INT[63].append(6)
		if POSITIVE_63.get() == 1:
			INT[63].append(7)
		if NEGATIVE_63.get() == 1:
			INT[63].append(8)
		if HALOGEN_63.get() == 1:
			INT[63].append(9)
		if HBD_64.get() == 1:
			INT[64].append(1)
		if HBA_64.get() == 1:
			INT[64].append(2)
		if HYDRO_64.get() == 1:
			INT[64].append(3)
		if PIPIP_64.get() == 1:
			INT[64].append(4)
		if PIPIT_64.get() == 1:
			INT[64].append(5)
		if PICAT_64.get() == 1:
			INT[64].append(6)
		if POSITIVE_64.get() == 1:
			INT[64].append(7)
		if NEGATIVE_64.get() == 1:
			INT[64].append(8)
		if HALOGEN_64.get() == 1:
			INT[64].append(9)
		if HBD_65.get() == 1:
			INT[65].append(1)
		if HBA_65.get() == 1:
			INT[65].append(2)
		if HYDRO_65.get() == 1:
			INT[65].append(3)
		if PIPIP_65.get() == 1:
			INT[65].append(4)
		if PIPIT_65.get() == 1:
			INT[65].append(5)
		if PICAT_65.get() == 1:
			INT[65].append(6)
		if POSITIVE_65.get() == 1:
			INT[65].append(7)
		if NEGATIVE_65.get() == 1:
			INT[65].append(8)
		if HALOGEN_65.get() == 1:
			INT[65].append(9)
		if HBD_66.get() == 1:
			INT[66].append(1)
		if HBA_66.get() == 1:
			INT[66].append(2)
		if HYDRO_66.get() == 1:
			INT[66].append(3)
		if PIPIP_66.get() == 1:
			INT[66].append(4)
		if PIPIT_66.get() == 1:
			INT[66].append(5)
		if PICAT_66.get() == 1:
			INT[66].append(6)
		if POSITIVE_66.get() == 1:
			INT[66].append(7)
		if NEGATIVE_66.get() == 1:
			INT[66].append(8)
		if HALOGEN_66.get() == 1:
			INT[66].append(9)
		if HBD_67.get() == 1:
			INT[67].append(1)
		if HBA_67.get() == 1:
			INT[67].append(2)
		if HYDRO_67.get() == 1:
			INT[67].append(3)
		if PIPIP_67.get() == 1:
			INT[67].append(4)
		if PIPIT_67.get() == 1:
			INT[67].append(5)
		if PICAT_67.get() == 1:
			INT[67].append(6)
		if POSITIVE_67.get() == 1:
			INT[67].append(7)
		if NEGATIVE_67.get() == 1:
			INT[67].append(8)
		if HALOGEN_67.get() == 1:
			INT[67].append(9)
		if HBD_68.get() == 1:
			INT[68].append(1)
		if HBA_68.get() == 1:
			INT[68].append(2)
		if HYDRO_68.get() == 1:
			INT[68].append(3)
		if PIPIP_68.get() == 1:
			INT[68].append(4)
		if PIPIT_68.get() == 1:
			INT[68].append(5)
		if PICAT_68.get() == 1:
			INT[68].append(6)
		if POSITIVE_68.get() == 1:
			INT[68].append(7)
		if NEGATIVE_68.get() == 1:
			INT[68].append(8)
		if HALOGEN_68.get() == 1:
			INT[68].append(9)
		if HBD_69.get() == 1:
			INT[69].append(1)
		if HBA_69.get() == 1:
			INT[69].append(2)
		if HYDRO_69.get() == 1:
			INT[69].append(3)
		if PIPIP_69.get() == 1:
			INT[69].append(4)
		if PIPIT_69.get() == 1:
			INT[69].append(5)
		if PICAT_69.get() == 1:
			INT[69].append(6)
		if POSITIVE_69.get() == 1:
			INT[69].append(7)
		if NEGATIVE_69.get() == 1:
			INT[69].append(8)
		if HALOGEN_69.get() == 1:
			INT[69].append(9)
		if HBD_70.get() == 1:
			INT[70].append(1)
		if HBA_70.get() == 1:
			INT[70].append(2)
		if HYDRO_70.get() == 1:
			INT[70].append(3)
		if PIPIP_70.get() == 1:
			INT[70].append(4)
		if PIPIT_70.get() == 1:
			INT[70].append(5)
		if PICAT_70.get() == 1:
			INT[70].append(6)
		if POSITIVE_70.get() == 1:
			INT[70].append(7)
		if NEGATIVE_70.get() == 1:
			INT[70].append(8)
		if HALOGEN_70.get() == 1:
			INT[70].append(9)
		if HBD_71.get() == 1:
			INT[71].append(1)
		if HBA_71.get() == 1:
			INT[71].append(2)
		if HYDRO_71.get() == 1:
			INT[71].append(3)
		if PIPIP_71.get() == 1:
			INT[71].append(4)
		if PIPIT_71.get() == 1:
			INT[71].append(5)
		if PICAT_71.get() == 1:
			INT[71].append(6)
		if POSITIVE_71.get() == 1:
			INT[71].append(7)
		if NEGATIVE_71.get() == 1:
			INT[71].append(8)
		if HALOGEN_71.get() == 1:
			INT[71].append(9)
		if HBD_72.get() == 1:
			INT[72].append(1)
		if HBA_72.get() == 1:
			INT[72].append(2)
		if HYDRO_72.get() == 1:
			INT[72].append(3)
		if PIPIP_72.get() == 1:
			INT[72].append(4)
		if PIPIT_72.get() == 1:
			INT[72].append(5)
		if PICAT_72.get() == 1:
			INT[72].append(6)
		if POSITIVE_72.get() == 1:
			INT[72].append(7)
		if NEGATIVE_72.get() == 1:
			INT[72].append(8)
		if HALOGEN_72.get() == 1:
			INT[72].append(9)
		if HBD_73.get() == 1:
			INT[73].append(1)
		if HBA_73.get() == 1:
			INT[73].append(2)
		if HYDRO_73.get() == 1:
			INT[73].append(3)
		if PIPIP_73.get() == 1:
			INT[73].append(4)
		if PIPIT_73.get() == 1:
			INT[73].append(5)
		if PICAT_73.get() == 1:
			INT[73].append(6)
		if POSITIVE_73.get() == 1:
			INT[73].append(7)
		if NEGATIVE_73.get() == 1:
			INT[73].append(8)
		if HALOGEN_73.get() == 1:
			INT[73].append(9)
		if HBD_74.get() == 1:
			INT[74].append(1)
		if HBA_74.get() == 1:
			INT[74].append(2)
		if HYDRO_74.get() == 1:
			INT[74].append(3)
		if PIPIP_74.get() == 1:
			INT[74].append(4)
		if PIPIT_74.get() == 1:
			INT[74].append(5)
		if PICAT_74.get() == 1:
			INT[74].append(6)
		if POSITIVE_74.get() == 1:
			INT[74].append(7)
		if NEGATIVE_74.get() == 1:
			INT[74].append(8)
		if HALOGEN_74.get() == 1:
			INT[74].append(9)
		if HBD_75.get() == 1:
			INT[75].append(1)
		if HBA_75.get() == 1:
			INT[75].append(2)
		if HYDRO_75.get() == 1:
			INT[75].append(3)
		if PIPIP_75.get() == 1:
			INT[75].append(4)
		if PIPIT_75.get() == 1:
			INT[75].append(5)
		if PICAT_75.get() == 1:
			INT[75].append(6)
		if POSITIVE_75.get() == 1:
			INT[75].append(7)
		if NEGATIVE_75.get() == 1:
			INT[75].append(8)
		if HALOGEN_75.get() == 1:
			INT[75].append(9)
		if HBD_76.get() == 1:
			INT[76].append(1)
		if HBA_76.get() == 1:
			INT[76].append(2)
		if HYDRO_76.get() == 1:
			INT[76].append(3)
		if PIPIP_76.get() == 1:
			INT[76].append(4)
		if PIPIT_76.get() == 1:
			INT[76].append(5)
		if PICAT_76.get() == 1:
			INT[76].append(6)
		if POSITIVE_76.get() == 1:
			INT[76].append(7)
		if NEGATIVE_76.get() == 1:
			INT[76].append(8)
		if HALOGEN_76.get() == 1:
			INT[76].append(9)
		if HBD_77.get() == 1:
			INT[77].append(1)
		if HBA_77.get() == 1:
			INT[77].append(2)
		if HYDRO_77.get() == 1:
			INT[77].append(3)
		if PIPIP_77.get() == 1:
			INT[77].append(4)
		if PIPIT_77.get() == 1:
			INT[77].append(5)
		if PICAT_77.get() == 1:
			INT[77].append(6)
		if POSITIVE_77.get() == 1:
			INT[77].append(7)
		if NEGATIVE_77.get() == 1:
			INT[77].append(8)
		if HALOGEN_77.get() == 1:
			INT[77].append(9)
		if HBD_78.get() == 1:
			INT[78].append(1)
		if HBA_78.get() == 1:
			INT[78].append(2)
		if HYDRO_78.get() == 1:
			INT[78].append(3)
		if PIPIP_78.get() == 1:
			INT[78].append(4)
		if PIPIT_78.get() == 1:
			INT[78].append(5)
		if PICAT_78.get() == 1:
			INT[78].append(6)
		if POSITIVE_78.get() == 1:
			INT[78].append(7)
		if NEGATIVE_78.get() == 1:
			INT[78].append(8)
		if HALOGEN_78.get() == 1:
			INT[78].append(9)
		if HBD_79.get() == 1:
			INT[79].append(1)
		if HBA_79.get() == 1:
			INT[79].append(2)
		if HYDRO_79.get() == 1:
			INT[79].append(3)
		if PIPIP_79.get() == 1:
			INT[79].append(4)
		if PIPIT_79.get() == 1:
			INT[79].append(5)
		if PICAT_79.get() == 1:
			INT[79].append(6)
		if POSITIVE_79.get() == 1:
			INT[79].append(7)
		if NEGATIVE_79.get() == 1:
			INT[79].append(8)
		if HALOGEN_79.get() == 1:
			INT[79].append(9)
		if HBD_80.get() == 1:
			INT[80].append(1)
		if HBA_80.get() == 1:
			INT[80].append(2)
		if HYDRO_80.get() == 1:
			INT[80].append(3)
		if PIPIP_80.get() == 1:
			INT[80].append(4)
		if PIPIT_80.get() == 1:
			INT[80].append(5)
		if PICAT_80.get() == 1:
			INT[80].append(6)
		if POSITIVE_80.get() == 1:
			INT[80].append(7)
		if NEGATIVE_80.get() == 1:
			INT[80].append(8)
		if HALOGEN_80.get() == 1:
			INT[80].append(9)
		if HBD_81.get() == 1:
			INT[81].append(1)
		if HBA_81.get() == 1:
			INT[81].append(2)
		if HYDRO_81.get() == 1:
			INT[81].append(3)
		if PIPIP_81.get() == 1:
			INT[81].append(4)
		if PIPIT_81.get() == 1:
			INT[81].append(5)
		if PICAT_81.get() == 1:
			INT[81].append(6)
		if POSITIVE_81.get() == 1:
			INT[81].append(7)
		if NEGATIVE_81.get() == 1:
			INT[81].append(8)
		if HALOGEN_81.get() == 1:
			INT[81].append(9)
		if HBD_82.get() == 1:
			INT[82].append(1)
		if HBA_82.get() == 1:
			INT[82].append(2)
		if HYDRO_82.get() == 1:
			INT[82].append(3)
		if PIPIP_82.get() == 1:
			INT[82].append(4)
		if PIPIT_82.get() == 1:
			INT[82].append(5)
		if PICAT_82.get() == 1:
			INT[82].append(6)
		if POSITIVE_82.get() == 1:
			INT[82].append(7)
		if NEGATIVE_82.get() == 1:
			INT[82].append(8)
		if HALOGEN_82.get() == 1:
			INT[82].append(9)
		if HBD_83.get() == 1:
			INT[83].append(1)
		if HBA_83.get() == 1:
			INT[83].append(2)
		if HYDRO_83.get() == 1:
			INT[83].append(3)
		if PIPIP_83.get() == 1:
			INT[83].append(4)
		if PIPIT_83.get() == 1:
			INT[83].append(5)
		if PICAT_83.get() == 1:
			INT[83].append(6)
		if POSITIVE_83.get() == 1:
			INT[83].append(7)
		if NEGATIVE_83.get() == 1:
			INT[83].append(8)
		if HALOGEN_83.get() == 1:
			INT[83].append(9)
		if HBD_84.get() == 1:
			INT[84].append(1)
		if HBA_84.get() == 1:
			INT[84].append(2)
		if HYDRO_84.get() == 1:
			INT[84].append(3)
		if PIPIP_84.get() == 1:
			INT[84].append(4)
		if PIPIT_84.get() == 1:
			INT[84].append(5)
		if PICAT_84.get() == 1:
			INT[84].append(6)
		if POSITIVE_84.get() == 1:
			INT[84].append(7)
		if NEGATIVE_84.get() == 1:
			INT[84].append(8)
		if HALOGEN_84.get() == 1:
			INT[84].append(9)
		if HBD_85.get() == 1:
			INT[85].append(1)
		if HBA_85.get() == 1:
			INT[85].append(2)
		if HYDRO_85.get() == 1:
			INT[85].append(3)
		if PIPIP_85.get() == 1:
			INT[85].append(4)
		if PIPIT_85.get() == 1:
			INT[85].append(5)
		if PICAT_85.get() == 1:
			INT[85].append(6)
		if POSITIVE_85.get() == 1:
			INT[85].append(7)
		if NEGATIVE_85.get() == 1:
			INT[85].append(8)
		if HALOGEN_85.get() == 1:
			INT[85].append(9)
		#~~ delete empty key and value pair
		for f in list(INT.keys()):
			if len(INT[f]) == 0: 
				del INT[f]
		if len(INT) == 0:
			tkinter.messagebox.showinfo("Warning","Please provide the filteration criteria!")
			return
		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		asd=open('input.txt','w')
		for f in list(INT.keys()):
			temp=str(f)
			for ff in INT[f]:
				if ff == 1:
					temp+='\t'+'HBD'
				if ff == 2:
					temp+='\t'+'HBA'
				if ff == 3:
					temp+='\t'+'HYDRO'
				if ff == 4:
					temp+='\t'+'PIPI_P'
				if ff == 5:
					temp+='\t'+'PIPI_T'
				if ff == 6:
					temp+='\t'+'PICAT'
				if ff == 7:
					temp+='\t'+'POSITIVE'
				if ff == 8:
					temp+='\t'+'NEGATIVE'
				if ff == 9:
					temp+='\t'+'HALOGEN'
			asd.write(temp+'\n')
		asd.close()
		asd=open('../'+filename,'r')
		FILE1=asd.readlines()
		asd.close()
#~~~~~~~~~~ PLIP Filtering: Begin ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		INTDICT={}
		# 1:HBD, 2:HBA, 3:Hydrophobic, 4:PIPI_P, 5:PIPI_T, 6:PICAT, 7:POSITIVE, 8:NEGATIVE, 9:HALOGEN
		FILE_ID=[]	#PDB structure name
		ENERGY={}	# Energy
		TOTAL={}	# Total number of criteria passed counting
		TOTALINT={}	# Total interaction from docked complex
		RESNUM={}	# Pocket index number
		DFG={}		# DFG-position
		aC={}		#alpha-C helix position
		SINGLE_REP_LIST={}	#Single_rep_structure name without poses
		#~~~ Initialization
		for f in FILE1:
			RESNUM[f.split()[0]+'_'+f.split()[1]]=[]
			TOTAL[f.split()[0]+'_'+f.split()[1]]=0
			ENERGY[f.split()[0]+'_'+f.split()[1]]=""
			DFG[f.split()[0]+'_'+f.split()[1]]=""
			aC[f.split()[0]+'_'+f.split()[1]]=""
		#~~ 
		#~~~~~~~~~~
		def inum_dict(i):
			if i == 8:
				return 1
			if i == 9:
				return 2
			if i == 10:
				return 3
			if i == 11:
				return 4
			if i == 12:
				return 5
			if i == 13:
				return 6
			if i == 14:
				return 7
			if i == 15:
				return 8
			if i == 16:
				return 9

		#~~~~~~~~~~
		for f in INT.keys():
			for ff in {'HBD','HBA','HYDRO','PIPI_P','PIPI_T','PICAT','POSITIVE','NEGATIVE','HALOGEN'}:
				INTDICT[ff]=[]
			for zz in INT[f]:
				if zz == 1:
					INTDICT["HBD"].append('1')
				elif zz == 2:
					INTDICT["HBA"].append('1')
				elif zz == 3:
					INTDICT["HYDRO"].append('1')
				elif zz == 4:
					INTDICT["PIPI_P"].append('1')
				elif zz == 5:
					INTDICT["PIPI_T"].append('1')
				elif zz == 6:
					INTDICT["PICAT"].append('1')
				elif zz == 7:
					INTDICT["POSITIVE"].append('1')
				elif zz == 8:
					INTDICT["NEGATIVE"].append('1')
				elif zz == 9:
					INTDICT["HALOGEN"].append('1')
			for ff in FILE1:
				if ff.split()[7] == str(f):
					for zz in INTDICT.keys():
						if len(INTDICT[zz]) != 0:
							if zz == 'HBD':
								inum=8
							if zz == 'HBA':
								inum=9
							if zz == 'HYDRO':
								inum=10
							if zz == 'PIPI_P':
								inum=11
							if zz == 'PIPI_T':
								inum=12
							if zz == 'PICAT':
								inum=13
							if zz == 'POSITIVE':
								inum=14
							if zz == 'NEGATIVE':
								inum=15
							if zz == 'HALOGEN':
								inum=16
							if ff.split()[inum] != '0':
								RESNUM[ff.split()[0]+'_'+ff.split()[1]].append(str(f)+'_'+str(inum_dict(inum)))
								TOTAL[ff.split()[0]+'_'+ff.split()[1]]+=1	#Count number of matching pattern from input
								ENERGY[ff.split()[0]+'_'+ff.split()[1]]=float(ff.split()[4])
								TOTALINT[ff.split()[0]+'_'+ff.split()[1]]=int(ff.split()[5])
								DFG[ff.split()[0]+'_'+ff.split()[1]]=ff.split()[2]
								aC[ff.split()[0]+'_'+ff.split()[1]]=ff.split()[3]
								SINGLE_REP_LIST[ff.split()[0]]=[]	#Single_rep_structure name without poses
		LIST=[]
		SORTARR=[]
		KININTERACTION={}
		KINENERGY={}
		LIST_STR_SORT={}
		for f in set(sorted(TOTAL.keys())):
			if TOTAL[f] != 0:
				LIST.append(TOTAL[f])
				tyu=[]
				tyu.append(f);tyu.append(DFG[f]);tyu.append(aC[f]);tyu.append(ENERGY[f]);tyu.append(TOTALINT[f]);tyu.append(TOTAL[f]);tyu.extend(RESNUM[f])
				LIST_STR_SORT[TOTAL[f]]=[]
				SINGLE_REP_LIST['_'.join(f.split('_')[:-1])].append(tyu)
		#~~~ For all poses: Start ~~~
		INPUT_KEYS=[]
		for f in sorted(INT.keys()):
			for ff in sorted(INT[f]):
				INPUT_KEYS.append(str(f)+'_'+str(ff))
		FAMILY={'AGC': ['MASTL', 'RSK4', 'NDR1', 'MSK1', 'BARK1', 'PKCt', 'YANK1', 'PKCa', 'DMPK1', 'GPRK5', 'PKCh', 'AKT1', 'PKN1', 'SGK1', 'ROCK1', 'MRCKb', 'PKCb', 'GPRK6', 'AKT2', 'PKN2', 'p70S6K', 'RSK2', 'PKCi', 'GPRK4', 'PKACa', 'ROCK2', 'RSK1', 'PDK1', 'PKG1'], 'Atypical': ['FRAP', 'PI4KB', 'RIOK1', 'PI4K2B', 'PI4K2A', 'ADCK3', 'DNAPK', 'p110d', 'ATR', 'ATM', 'p110a', 'PI4KA', 'RIOK2', 'p110b', 'p110g', 'PIK3C3'], 'CAMK': ['CASK', 'TTN', 'AMPKa2', 'MARK3', 'SgK495', 'MARK1', 'CaMK2g', 'DAPK3', 'DRAK2', 'SgK085', 'MAPKAPK2', 'CHK1', 'AMPKa1', 'CaMK4', 'PIM2', 'PHKg2', 'CaMK1a', 'RSK2-b', 'CaMK1d', 'RSK1-b', 'MAPKAPK3', 'MNK1', 'CaMK2d', 'Trb1', 'CaMK1g', 'BRSK2', 'PIM1', 'DAPK2', 'CaMK2a', 'LKB1', 'MNK2', 'MELK', 'CaMK2b', 'DCLK1', 'PASK', 'DAPK1', 'SNRK', 'MARK2', 'CHK2', 'MSK1-b', 'MARK4'], 'CK1': ['CK1e', 'CK1g1', 'VRK3', 'VRK1', 'CK1g3', 'VRK2', 'CK1d', 'TTBK1', 'CK1a', 'CK1g2'], 'CMGC': ['CDKL3', 'CDK9', 'Erk1', 'PCTAIRE1', 'JNK2', 'CHED', 'JNK1', 'CDK8', 'CRK7', 'CDKL1', 'CLK2', 'CLK4', 'DYRK2', 'p38b', 'p38d', 'CK2a2', 'SRPK1', 'CDK7', 'DYRK1A', 'p38g', 'CDKL2', 'JNK3', 'SRPK2', 'DYRK3', 'Erk2', 'p38a', 'GSK3B', 'PRP4', 'CDK6', 'Erk5', 'CDC2', 'CLK3', 'CK2a1', 'CDK5', 'CDK2', 'CDK4', 'CDKL5', 'CLK1', 'HIPK2', 'Erk3'], 'Other': ['PLK2', 'PLK1', 'NEK2', 'SgK223', 'GCN2', 'GAK', 'CaMKK1', 'ULK1', 'AurA', 'Wnk3', 'AurB', 'NEK7', 'MYT1', 'IRE1', 'MPSK1', 'CaMKK2', 'IKKb', 'ULK2', 'CDC7', 'Haspin', 'BUB1', 'IKKa', 'AAK1', 'PKR', 'Wee1', 'TTK', 'NEK1', 'PBK', 'PEK', 'RNAseL', 'SGK196', 'BIKE', 'SgK269', 'AurC', 'Wnk1', 'PLK4', 'PLK3', 'Wee1B', 'ULK3', 'TBK1', 'TLK2'], 'STE': ['PAK4', 'NIK', 'LOK', 'PAK1', 'MAP2K6', 'MST4', 'MST2', 'MAP2K1', 'STLK3', 'HGK', 'PAK3', 'MST3', 'MST1', 'MAP3K5', 'SLK', 'MAP2K4', 'HPK1', 'KHS2', 'OSR1', 'TNIK', 'YSK1', 'MAP2K7', 'COT', 'PAK6', 'MAP2K2', 'STLK5', 'PAK5', 'TAO3'], 'TK': ['ErbB2', 'FGFR3', 'ErbB3', 'FMS', 'MET', 'RON', 'ROS', 'ZAP70', 'FGFR2', 'EphA2', 'FLT1', 'IGF1R', 'ACK', 'JAK1-b', 'TYK2-b', 'INSR', 'FLT3', 'PYK2', 'PDGFRb', 'TIE2', 'EphB3', 'LCK', 'ErbB4', 'EphA5', 'JAK2', 'AXL', 'BRK', 'DDR1', 'SRC', 'JAK2-b', 'SYK', 'KIT', 'FES', 'ALK', 'HCK', 'ITK', 'LYN', 'EphA7', 'EphA3', 'TRKC', 'TYK2', 'ABL1', 'EGFR', 'JAK1', 'MER', 'CSK', 'ABL2', 'TRKA', 'BTK', 'RET', 'PDGFRa', 'EphB4', 'ROR2', 'FGFR1', 'FYN', 'BMX', 'JAK3', 'FAK', 'KDR', 'DDR2', 'EphB2', 'TYRO3', 'EphB1', 'EphA4', 'EphA8', 'FGFR4', 'TRKB'], 'TKL': ['MLKL', 'IRAK1', 'HH498', 'TGFbR1', 'DLK', 'LIMK1', 'ANKRD3', 'BMPR1B', 'IRAK4', 'KSR2', 'LIMK2', 'ACTR2B', 'RIPK2', 'RIPK1', 'BRAF', 'ACTR2', 'MLK1', 'TGFbR2', 'BMPR2', 'TAK1', 'ZAK', 'RIPK3', 'MLK4', 'ILK', 'RAF1', 'ALK2', 'ALK1']}
		#~~ Mutation Information: Start
		MUTATION={}
		asd=open(KINASE_DB+'/Mutation.txt','r')
		mutinfo=asd.readlines()
		asd.close()
		for f in mutinfo:
			MUTATION['_'.join(f.split('_')[0:2])]='_'.join(f.split('_')[2:]).strip('\n')
		#~~ Mutation Information: End
		asd=open('All_pose_structure.txt','w')
		##~~~~~~~ Header: START ~~~~~~~~~~
		ghj='Struct_Name\tPose_Num\tFamily\tMutation\tDFG\taC\tEnergy\tTotal_Int\tInt_pattern'
		a=1
		for f in sorted(INT.keys()):
			for ff in sorted(INT[f]):
				ghj+='\t'+'Option_'+str(a)
				a+=1
		asd.write(ghj+'\n')
		##~~~~~~~ Header: END ~~~~~~~~~~
		for z in SINGLE_REP_LIST.keys():
			for f in SINGLE_REP_LIST[z]:
				temp='_'.join(f[0].split('_')[:-1])+'\t'+f[0].split('_')[-1]
				#~~~ Family: Start
				for s in FAMILY.keys():
					if f[0].split('_')[0] in FAMILY[s]:
						temp+='\t'+s
				#~~~ Family: End
				#~~~ Mutation: Start
				if f[0].split('_')[1]+'_'+f[0].split('_')[-2][-1] in MUTATION.keys():	#Mutation
					temp+='\t'+MUTATION[f[0].split('_')[1]+'_'+f[0].split('_')[-2][-1]]
				else:
					temp+='\t'+'-'
				#~~~ Mutation: End
				for r in f[1:6]:
					temp+='\t'+str(r)
				for e in INPUT_KEYS:
					if e in f[6:]:
						temp+='\t'+e
					else:
						temp+='\t'+'-'
				asd.write(temp+'\n')
		asd.close()
		#~~~~~ For all poses: END ~~~~~~~~~
		#~~~ Single rep from all 20 poses: Start
		FINAL_STR_LIST=[]
		INT_PATTERN={}
		for f in set(sorted(LIST)):
			INT_PATTERN[int(f)]=[]

		GENE_SORT={}
		GENE_INT={}
		GENE={}
		for f in sorted(SINGLE_REP_LIST.keys()):
			BEST_INT=[]
			for ff in SINGLE_REP_LIST[f]:
				BEST_INT.append(int(ff[5]))
			highest_int=max(BEST_INT)
			best_int_from_pose=[]
			for ff in SINGLE_REP_LIST[f]:
				if ff[5] == highest_int:
					best_int_from_pose.append(ff)
			for ff in sorted(best_int_from_pose, key = lambda x:(x[3],-x[4])):
				LIST_STR_SORT[int(ff[5])].append(ff)
				GENE_SORT[ff[0].split('_')[0]]=[]
				GENE_INT[ff[0].split('_')[0]]=[]
				GENE[int(ff[5])]=[]
				break

		INPUT_KEYS=[]
		for f in sorted(INT.keys()):
			for ff in sorted(INT[f]):
				INPUT_KEYS.append(str(f)+'_'+str(ff))
		asd=open('Best_pose_structure.txt','w')
		ghj='Struct_Name\tPose_Num\tFamily\tMutation\tDFG\taC\tEnergy\tTotal_Int\tInt_pattern'
		a=1
		for f in sorted(INT.keys()):
			for ff in sorted(INT[f]):
				ghj+='\t'+'Option_'+str(a)
				a+=1
		asd.write(ghj+'\n')
		for z in sorted(LIST_STR_SORT.keys(),reverse=True):
			for f in sorted(LIST_STR_SORT[z],key= lambda x:(x[3],-x[4])):
				GENE_SORT[f[0].split('_')[0]].append(f)
				GENE_INT[f[0].split('_')[0]].append(f[5])
				temp='_'.join(f[0].split('_')[:-1])+'\t'+f[0].split('_')[-1]
				#~~~ Family: Start
				for s in FAMILY.keys():
					if f[0].split('_')[0] in FAMILY[s]:
						temp+='\t'+s
				#~~~ Family: End
				#~~~ Mutation: Start
				if f[0].split('_')[1]+'_'+f[0].split('_')[-2][-1] in MUTATION.keys():	#Mutation
					temp+='\t'+MUTATION[f[0].split('_')[1]+'_'+f[0].split('_')[-2][-1]]
				else:
					temp+='\t'+'-'
				#~~~ Mutation: End
				for r in f[1:6]:
					temp+='\t'+str(r)
				for e in INPUT_KEYS:
					if e in f[6:]:
						temp+='\t'+e
					else:
						temp+='\t'+'-'
				asd.write(temp+'\n')
		asd.close()
		#~~~ Single rep from all 20 poses: END
		#~~~ Best protein-based ranking: Start
		asd=open('Protein_list.txt','w')
		ghj='Protein_Name\tFamily\tMutation\tDFG\taC\tEnergy\tTotal_Int\tInt_pattern'
		a=1
		for f in sorted(INT.keys()):
			for ff in sorted(INT[f]):
				ghj+='\t'+'Option_'+str(a)
				a+=1
		asd.write(ghj+'\n')
		for f in sorted(GENE_SORT.keys()):
			highest_gene=max(GENE_INT[f])
			best_gene_pose=[]
			for ff in GENE_SORT[f]:
				if ff[5] == highest_gene:
					best_gene_pose.append(ff)
			for ff in sorted(best_gene_pose, key= lambda x:(x[3],-x[4])):
				GENE[ff[5]].append(ff)
				break
		for z in sorted(GENE.keys(),reverse=True):
			for f in sorted(GENE[z],key=lambda x:(x[3],-x[4])):
				temp=f[0].split('_')[0]
				#~~~ Family: Start
				for s in FAMILY.keys():
					if f[0].split('_')[0] in FAMILY[s]:
						temp+='\t'+s
				#~~~ Family: End
				#~~~ Mutation: Start
				if f[0].split('_')[1]+'_'+f[0].split('_')[-2][-1] in MUTATION.keys():	#Mutation
					temp+='\t'+MUTATION[f[0].split('_')[1]+'_'+f[0].split('_')[-2][-1]]
				else:
					temp+='\t'+'-'
				#~~~ Mutation: End
				for r in f[1:6]:
					temp+='\t'+str(r)
				for e in INPUT_KEYS:
					if e in f[6:]:
						temp+='\t'+e
					else:
						temp+='\t'+'-'
				asd.write(temp+'\n')
		asd.close()
		Analysiscount+=1
		run_kinomerender(filename)
		#~~~ Best protein-based ranking: END
	#~~~~~~ Kinomerender: start
	def run_kinomerender(filename):
		global analysisworking
		KINOME={'Abl':['ABL','ABL1','ABL','JTK7'],'Ack':['ACK','TNK2','ACK1'],'ACtR2':['ACTR2','ACVR2A','ACVR2'],'ACtR2B':['ACTR2B','ACVR2B'],'ADCK4':['ADCK4','ADCK4'],'Trb1':['Trb1','TRIB1','C8FW','GIG2','TRB1'],'BRSK2':['BRSK2','BRSK2','C11orf7','PEN11B','SADA','STK29','ORF Names:','HUSSY-12'],'WNK2':['Wnk2','WNK2'],'Akt1/PKB[alpha]':['AKT1','AKT1','PKB','RAC'],'Akt2/PKB[beta]':['AKT2','AKT2'],'Akt3/PKB[gamma]':['AKT3','AKT3','PKBG'],'CaMK1[gamma]':['CaMK1g','CAMK1G','VWS1'],'ALK':['ALK','ALK'],'ALK1':['ALK1','ACVRL1','ACVRLK1','ALK1'],'ALK2':['ALK2','ACVR1','ACVRLK2'],'BMPR1A':['BMPR1A','BMPR1A','ACVRLK3','ALK3'],'ALK4':['ALK4','ACVR1B','ACVRLK4','ALK4'],'TGF[beta]R1':['TGFbR1','TGFBR1','ALK5','SKR4'],'BMPR1B':['BMPR1B','BMPR1B'],'AMPK[alpha]1':['AMPKa1','PRKAA1','AMPK1'],'AMPK[alpha]2':['AMPKa2','PRKAA2','AMPK','AMPK2'],'ANP[alpha]':['ANPa','NPR1','ANPRA'],'ANP[beta]':['ANPb','NPR2','ANPRB'],'ARAF':['ARAF','ARAF','ARAF1','PKS','PKS2'],'Arg':['ARG','ABL2','ABLL','ARG'],'ATM':['ATM','ATM'],'ATR':['ATR','ATR','FRP1'],'AurC/Aur3':['AurC','AURKC','AIE2','AIK3','AIRK3','ARK3','STK13'],'Axl':['AXL','AXL','UFO'],'BARK1/GRK2':['BARK1','ADRBK1','BARK','BARK1','GRK2'],'BCKDK':['BCKDK','BCKDK'],'GCK':['GCK','MAP4K2','GCK','RAB8IP'],'BLK':['BLK','BLK'],'BRAF':['BRAF','BRAF','BRAF1','RAFB1'],'Brk':['BRK','PTK6','BRK'],'BTK':['BTK','BTK','AGMX1','ATK','BPK'],'BubR1':['BUBR1','BUB1B','BUBR1','MAD3L','SSK1'],'CDK7':['CDK7','CDK7','CAK','CAK1','CDKN7','MO15','STK1'],'CaMK1[alpha]':['CaMK1a','CAMK1'],'CaMK2[alpha]':['CaMK2a','CAMK2A','CAMKA','KIAA0968'],'CaMK2[beta]':['CaMK2b','CAMK2B','CAM2','CAMK2','CAMKB'],'CaMK2[gamma]':['CaMK2g','CAMK2G','EMBL CAI13967.1','ORF Names:','hCG_20541','EMBL EAW54540.1','','RP11-574K11.6-004','EMBL CAI13967.1'],'CaMK4':['CaMK4','CAMK4','CAMK','CAMK-GR','CAMKIV'],'VACAMKL':['VACAMKL','CAMKV'],'DCAMKL1':['DCAMKL1','DCLK1','DCAMKL1','DCDC3A','KIAA0369'],'CASK':['CASK','CASK','LIN2'],'CDC2/CDK1':['CDC2','CDK1','CDC2','CDC28A','CDKN1','P34CDC2'],'CDC7':['CDC7','CDC7','CDC7L1'],'CDK2':['CDK2','CDK2','CDKN2'],'CDK3':['CDK3','CDK3','CDKN3'],'CDK4':['CDK4','CDK4'],'CDK5':['CDK5','CDK5','CDKN5'],'CDK6':['CDK6','CDK6','CDKN6'],'CDK8':['CDK8','CDK8'],'PKG1':['PKG1','PRKG1','PRKG1B','PRKGR1A','PRKGR1B'],'PKG2':['PKG2','PRKG2','PRKGR2'],'CHED':['CHED','CDK13','CDC2L','CDC2L5','CHED','KIAA1791'],'CHK1':['CHK1','CHEK1','CHK1'],'CHK2':['CHK2','CHEK2','CDS1','CHK2','RAD53'],'CK1[alpha]':['CK1a','CSNK1A1'],'CK1[delta]':['CK1d','CSNK1D','HCKID'],'CK1[epsilon]':['CK1e','CSNK1E'],'CK1[gamma]2':['CK1g2','CSNK1G2','CK1G2'],'CK1[gamma]3':['CK1g3','CSNK1G3'],'CK2[alpha]1':['CK2a1','CSNK2A1','CK2A1'],'CK2[alpha]2':['CK2a2','CSNK2A2','CK2A2'],'CLK1':['CLK1','CLK1','CLK'],'CLK2':['CLK2','CLK2'],'CLK3':['CLK3','CLK3'],'COT':['COT','MAP3K8','COT','ESTF'],'FmS/CSFR':['FMS','CSF1R','FMS'],'CSK':['CSK','CSK'],'MARK3':['MARK3','MARK3','CTAK1','EMK2'],'CYGD':['CYGD','GUCY2D','CORD6','GUC1A4','GUC2D','RETGC','RETGC1'],'CYGF':['CYGF','GUCY2F','GUC2F','RETGC2'],'DAPK1':['DAPK1','DAPK1','DAPK'],'DAPK2':['DAPK2','DAPK2'],'DLK':['DLK','MAP3K12','ZPK'],'DMPK':['DMPK1','DMPK','DM1PK','MDPK'],'DMPK2':['DMPK2','CDC42BPG','DMPK2'],'DNAPK':['DNAPK','PRKDC','HYRC','HYRC1'],'DYRK1B':['DYRK1B','DYRK1B','MIRK'],'DYRK2':['DYRK2','DYRK2'],'DYRK4':['DYRK4','DYRK4'],'EEF2K':['eEF2K','EEF2K'],'EGFR':['EGFR','EGFR','ERBB','ERBB1','HER1'],'PKR':['PKR','EIF2AK2','PKR','PRKR'],'MARK2':['MARK2','MARK2','EMK1'],'EphA1':['EphA1','EPHA1','EPH','EPHT','EPHT1'],'EphA2':['EphA2','EPHA2','ECK'],'EphA3':['EphA3','EPHA3','ETK','ETK1','HEK','TYRO4'],'EphA4':['EphA4','EPHA4','HEK8','SEK','TYRO1'],'EphA5':['EphA5','EPHA5','BSK','EHK1','HEK7','TYRO4'],'EphA8':['EphA8','EPHA8','EEK','HEK3','KIAA1459'],'EphB1':['EphB1','EPHB1','ELK','EPHT2','HEK6','NET'],'EphB2':['EphB2','EPHB2','DRT','EPHT3','EPTH3','ERK','HEK5','TYRO5'],'EphB3':['EphB3','EPHB3','ETK2','HEK2','TYRO6'],'EphB4':['EphB4','EPHB4','HTK','MYK1','TYRO11'],'EphB6':['EphB6','EPHB6'],'ERK1':['Erk1','MAPK3','ERK1','PRKM3'],'ERK2':['Erk2','MAPK1','ERK2','PRKM1','PRKM2'],'ERK3':['Erk3','MAPK6','ERK3','PRKM6'],'ERK4':['Erk4','MAPK4','ERK4','PRKM4'],'FAK':['FAK','PTK2','FAK','FAK1'],'Fer':['FER','FER','TYK3'],'Fes':['FES','FES','FPS'],'FGFR1':['FGFR1','FGFR1','BFGFR','CEK','FGFBR','FLG','FLT2','HBGFR'],'FGFR2':['FGFR2','FGFR2','BEK','KGFR','KSAM'],'FGFR3':['FGFR3','FGFR3','JTK4'],'FGFR4':['FGFR4','FGFR4','JTK2','TKF'],'Fgr':['FGR','FGR','SRC2'],'FLT3':['FLT3','FLT3','CD135','FLK2','STK1'],'FLT1':['FLT1','FLT1','FLT','FRT','VEGFR1'],'FLT4':['FLT4','FLT4'],'mTOR/FRAP':['FRAP','MTOR','FRAP','FRAP1','FRAP2','RAFT1','RAPT1'],'Fyn':['FYN','FYN'],'GAK':['GAK','GAK'],'GRK4':['GPRK4','GRK4','GPRK2L','GPRK4'],'GRK5':['GPRK5','GRK5','GPRK5'],'GRK6':['GPRK6','GRK6','GPRK6'],'Trb2':['Trb2','TRIB2','TRB2'],'GSK3[alpha]':['GSK3A','GSK3A'],'GSK3[beta]':['GSK3B','GSK3B'],'HCK':['HCK','HCK'],'HER2':['HER2','ErbB2','ERBB2','HER2','MLN19','NEU','NGL'],'HER3':['HER3','ErbB3','ERBB3','HER3'],'HER4':['HER4','ErbB4','ERBB4','HER4'],'HIPK1':['HIPK1','HIPK1','KIAA0630','MYAK','NBAK2'],'HPK1':['HPK1','MAP4K1','HPK1'],'HSER':['HSER','GUCY2C','GUC2C','STAR'],'IGF1R':['IGF1R','IGF1R'],'IKK[alpha]':['IKKa','CHUK','IKKA','TCF16'],'IKK[beta]':['IKKb','IKBKB','IKKB'],'ILK':['ILK','ILK','ILK1','ILK2'],'InSR':['INSR','INSR'],'IRAK1':['IRAK1','IRAK1','IRAK'],'IRAK2':['IRAK2','IRAK2'],'IRAK3':['IRAK3','IRAK3'],'IRE1':['IRE1','ERN1','IRE1'],'IRR':['IRR','INSRR','IRR'],'ITK':['ITK','ITK','EMT','LYK'],'JAK1':['JAK1','JAK1','JAK1A','JAK1B'],'JAK2':['JAK2','JAK2'],'JAK3':['JAK3','JAK3'],'JNK1':['JNK1','MAPK8','JNK1','PRKM8','SAPK1','SAPK1C'],'JNK2':['JNK2','MAPK9','JNK2','PRKM9','SAPK1A'],'JNK3':['JNK3','MAPK10','JNK3','JNK3A','PRKM10','SAPK1B'],'KHS1':['KHS1','MAP4K5'],'IKK[epsilon]':['IKKe','IKBKE','IKKE','IKKI','KIAA0151'],'NuaK1':['NuaK1','NUAK1','ARK5','KIAA0537','OMPHK1'],'MAST3':['MAST3','MAST3','KIAA0561'],'Fused':['Fused','STK36','KIAA1278'],'Pim3':['PIM3','PIM3'],'Kit':['KIT','KIT','SCFR'],'CDKL2':['CDKL2','CDKL2'],'CDKL1':['CDKL1','CDKL1'],'KSR':['KSR1','CDKL1'],'Lck':['LCK','LCK'],'LIMK2':['LIMK2','LIMK2'],'Lkb1':['LKB1','STK11','LKB1','PJS'],'LTK':['LTK','LTK','TYK1'],'Lyn':['LYN','LYN','JTK8'],'MAK':['MAK','MAK'],'MAPKAPK2':['MAPKAPK2','MAPKAPK2'],'MAPKAPK3':['MAPKAPK3','MAPKAPK3'],'MAPKAPK5':['MAPKAPK5','PRAK','MAPKAPK5'],'MARK1':['MARK1','MARK1','KIAA1477','MARK'],'MAST2':['MAST2','MAST2','KIAA0807','MAST205'],'MEK1/MAP2K1':['MAP2K1','MAP2K1','MEK1','PRKMK1'],'MEK2/MAP2K2':['MAP2K2','MAP2K2','MEK2','MKK2','PRKMK2'],'MAP2K5':['MAP2K5','MAP2K5','MEK5','MKK5','PRKMK5'],'MKK6/MAP2K6':['MAP2K6','MAP2K6','MEK6','MKK6','PRKMK6','SKK3'],'MEKK1/MAP3K1':['MAP3K1','MAP3K1','MAPKKK1','MEKK','MEKK1'],'MEKK2/MAP3K2':['MAP3K2','MAP3K2','MAPKKK2','MEKK2'],'MEKK3/MAP3K3':['MAP3K3','MAP3K3','MAPKKK3','MEKK3'],'MAP3K4':['MAP3K4','MAP3K4','KIAA0213','MAPKKK4','MEKK4','MTK1'],'ASK/MAP3K5':['MAP3K5','MAP3K5','ASK1','MAPKKK5','MEKK5'],'Mer':['MER','MERTK','MER'],'Met':['MET','MET'],'MISR2':['MISR2','AMHR2','AMHR','MISR2'],'MAP2K7':['MAP2K7','MAP2K7','JNKK2','MEK7','MKK7','PRKMK7','SKK4'],'smMLCK':['smMLCK','MYLK','MLCK','MLCK1','MYLK1'],'MLK1':['MLK1','MAP3K9','MLK1','PRKE1'],'MLK2':['MLK2','MAP3K10','MLK2','MST'],'DYRK1A':['DYRK1A','DYRK1A','DYRK','MNB','MNBH'],'MNK1':['MNK1','MKNK1','MNK1'],'MNK2':['MNK2','MKNK2','GPRK7','MNK2'],'MOS':['MOS','MOS'],'MKK3/MAP2K3':['MAP2K3','MAP2K3','MEK3','MKK3','PRKMK3','SKK2'],'SEK1/MAP2K4':['MAP2K4','MAP2K4','JNKK1','MEK4','MKK4','PRKMK4','SEK1','SERK1','SKK1'],'MRCK[beta]':['MRCKb','CDC42BPB','KIAA1124'],'MSK1':['MSK1','RPS6KA5','MSK1'],'MSK2':['MSK2','RPS6KA4','MSK2'],'MST1':['MST1','STK4','KRS2','MST1'],'MST2':['MST2','STK3','KRS1','MST2'],'MST3':['MST3','STK24','MST3','STK3'],'MUSK':['MUSK','MUSK'],'MYT1':['MYT1','PKMYT1','MYT1'],'NDR1':['NDR1','STK38','NDR1'],'Nek1':['NEK1','NEK1','KIAA1901'],'Nek2':['NEK2','NEK2','NEK2A','NLK1'],'Nek3':['NEK3','NEK3'],'NIK':['NIK','MAP3K14','NIK'],'NLK':['NLK','NLK','LAK1'],'Nek4':['NEK4','NEK4','STK2'],'IRAK4':['IRAK4','IRAK4'],'PIK3R4':['PIK3R4','PIK3R4'],'ROCK2':['ROCK2','ROCK2','KIAA0619'],'p38[alpha]':['p38a','MAPK14','CSBP','CSBP1','CSBP2','CSPB1','MXI2','SAPK2A'],'p70S6K':['p70S6K','RPS6KB1','STK14A'],'p70S6K[beta]':['p70S6Kb','RPS6KB2','STK14B'],'PAK1':['PAK1','PAK1'],'PAK2':['PAK2','PAK2'],'PAK3':['PAK3','PAK3','OPHN3'],'PKC[eta]':['PKCh','PRKCH','PKCL','PRKCL'],'PCTAIRE1':['PCTAIRE1','CDK16','PCTK1'],'PCTAIRE2':['PCTAIRE2','CDK17','PCTK2'],'PCTAIRE3':['PCTAIRE3','CDK18','PCTK3'],'PDGFR[alpha]':['PDGFRa','PDGFRA','PDGFR2','RHEPDGFRA'],'PDGFR[beta]':['PDGFRb','PDGFRB','PDGFR','PDGFR1'],'PDK1':['PDK1','PDPK1','PDK1'],'PDHK1':['PDHK1','PDK1','PDHK1'],'PDHK2':['PDHK2','PDK2','PDHK2'],'PDHK3':['PDHK3','PDK3','PDHK3'],'PDHK4':['PDHK4','PDK4','PDHK4'],'PERK/PEK':['PEK','EIF2AK3','PEK','PERK'],'PFTAIRE1':['PFTAIRE1','CDK14','KIAA0834','PFTK1'],'PhK[gamma]1':['PHKg1','PHKG1','PHKG'],'PhK[gamma]2':['PHKg2','PHKG2'],'Pim1':['PIM1','PIM1'],'Pim2':['PIM2','PIM2'],'CDK10':['CDK10','CDK10'],'CDK9':['CDK9','CDK9','CDC2L4','TAK'],'PITSLRE':['PITSLRE','CDK11B','CDC2L1','CDK11','PITSLREA','PK58'],'MELK':['MELK','MELK','KIAA0175'],'MRCK[alpha]':['MRCKa','CDC42BPA','KIAA0451'],'PKA[alpha]':['PKACa','PRKACA','PKACA'],'PKA[beta]':['PKACb','PRKACB'],'PKA[gamma]':['PKACg','PRKACG'],'PKC[alpha]':['PKCa','PRKCA','PKCA','PRKACA'],'PKC[beta]':['PKCb','PRKCB','PKCB','PRKCB1'],'PKC[delta]':['PKCd','PRKCD'],'PKC[epsilon]':['PKCe','PRKCE','PKCE'],'PKC[gamma]':['PKCg','PRKCG','PKCG'],'PKC[iota]':['PKCi','PRKCI','DXS1179E'],'PKD1':['PKD1','PRKD1','PKD','PKD1','PRKCM'],'PKC[theta]':['PKCt','PRKCQ','PRKCT'],'PKC[zeta]':['PKCz','PRKCZ','PKC2'],'PRKX':['PRKX','PRKX','PKX1'],'HIPK3':['HIPK3','HIPK3','DYRK6','FIST3','PKY'],'PLK1':['PLK1','PLK1','PLK'],'PLK3':['PLK3','PLK3','CNK','FNK','PRK'],'PKN1/PRK1':['PKN1','PKN1','PAK1','PKN','PRK1','PRKCL1'],'PKN2/PRK2':['PKN2','PKN2','PRK2','PRKCL2'],'PRKY':['PRKY','PRKY'],'PRP4':['PRP4','PRPF4B','KIAA0536','PRP4','PRP4H','PRP4K'],'PSKH1':['PSKH1','PSKH1'],'RAF1':['RAF1','RAF1','RAF'],'Ret':['RET','RET','CDHF12','CDHR16','PTC','RET51'],'RHODK/GRK1':['RHOK','GRK1','RHOK'],'RIPK1':['RIPK1','RIPK1','RIP','RIP1'],'RIPK2':['RIPK2','RIPK2','CARDIAK','RICK','RIP2','ORF Names:','UNQ277/PRO314/PRO34092'],'RIPK3':['RIPK3','RIPK3','RIP3'],'ROCK1':['ROCK1','ROCK1'],'Ron':['RON','MST1R','PTK8','RON'],'ROR1':['ROR1','ROR1','NTRKR1'],'ROR2':['ROR2','ROR2','NTRKR2'],'Ros':['ROS','ROS1','MCF3','ROS'],'RSK1/p90RSK':['RSK1','RPS6KA2','MAPKAPK1C','RSK3'],'RSK2':['RSK2','RPS6KA3','ISPK1','MAPKAPK1B','RSK2'],'RSK3':['RSK3','RPS6KA1','MAPKAPK1A','RSK1'],'RYK':['RYK','RYK'],'PLK4':['PLK4','PLK4','SAK','STK18'],'p38[beta]':['p38b','MAPK11','PRKM11','SAPK2','SAPK2B'],'p38[gamma]':['p38g','MAPK12','ERK6','SAPK3'],'p38[delta]':['p38d','MAPK13','PRKM13','SAPK4'],'MAST1':['MAST1','MAST1','KIAA0973','SAST'],'SGK1':['SGK','SGK1','SGK'],'SLK':['SLK','SLK','KIAA0204','STK2'],'PLK2':['PLK2','PLK2','SNK'],'MLK3':['MLK3','MAP3K11','MLK3','PTK1','SPRK'],'Src':['SRC','SRC','SRC1'],'SRPK1':['SRPK1','SRPK1'],'SRPK2':['SRPK2','SRPK2'],'CDKL5':['CDKL5','CDKL5','STK9'],'TAO2':['TAO2','TAOK2','EMBL AAI44345.1'],'Syk':['SYK','SYK'],'TAK1':['TAK1','MAP3K7','TAK1'],'BMPR2':['BMPR2','BMPR2','PPH1'],'TEC':['TEC','TEC','PSCTK4'],'TIE2':['TIE2','TEK','TIE2','VMCM','VMCM1'],'TESK1':['TESK1','TESK1'],'TGF[beta]R2':['TGFbR2','TGFBR2'],'TIE1':['TIE1','TIE1','TIE'],'TTN':['TTN','TTN'],'TLK1':['TLK1','TLK1','KIAA0137'],'TLK2':['TLK2','TLK2'],'Tnk1':['TNK1','TNK1'],'Trio':['Trio','TRIO'],'TRKA':['TRKA','NTRK1','MTC','TRK','TRKA'],'TRKB':['TRKB','NTRK2','TRKB'],'TRKC':['TRKC','NTRK3','TRKC'],'TRRAP':['TRRAP','TRRAP','PAF400'],'TTK':['TTK','TTK','MPS1','MPS1L1'],'TXK':['TXK','TXK','PTK4','RLK'],'Tyk2':['TYK2','TYK2'],'Tyro3/Sky':['TYRO3','TYRO3','BYK','DTK','RSE','SKY'],'ULK1':['ULK1','ULK1','KIAA0722'],'ULK2':['ULK2','ULK2','KIAA0623'],'VRK1':['VRK1','VRK1'],'VRK2':['VRK2','VRK2'],'Wee1':['Wee1','WEE1'],'Yes':['YES','YES1','YES'],'YSK1':['YSK1','STK25','SOK1','YSK1'],'ZAP70':['ZAP70','ZAP70','SRK'],'LZK':['LZK','MAP3K13','LZK'],'DDR1':['DDR1','DDR1','CAK','EDDR1','NEP','NTRK4','PTK3A','RTK6','TRKE'],'ADCK1':['ADCK1','ADCK1'],'KDR':['KDR','KDR','FLK1','VEGFR2'],'ALK7':['ALK7','ACVR1C','ALK7'],'AurB/Aur1':['AurB','AURKB','AIK2','AIM1','AIRK2','ARK2','STK1','STK12','STK5'],'AurA/Aur2':['AurA','AURKA','AIK','AIRK1','ARK1','AURA','AYK1','BTAK','IAK1','STK15','STK6'],'ERK5':['Erk5','MAPK7','BMK1','ERK5','PRKM7'],'Bub1':['BUB1','BUB1','BUB1L'],'DDR2':['DDR2','DDR2','NTRKR3','TKT','TYRO10'],'CCK4/PTK7':['CCK4','PTK7','CCK4'],'LIMK1':['LIMK1','LIMK1','LIMK'],'Lmr1':['LMR1','AATK','AATYK','KIAA0641','LMR1','LMTK1'],'Lmr2':['LMR2','LMTK2','AATYK2','BREK','KIAA1079','KPI2','LMR2'],'Lmr3':['LMR3','LMTK3','KIAA1883','TYKLM3'],'EphA7':['EphA7','EPHA7','EHK3','HEK11'],'Etk/BMX':['BMX','BMX'],'CTK':['CTK','MATK','CTK','HYL'],'FRK':['FRK','FRK','PTK5','RAK'],'Nek6':['NEK6','NEK6'],'Nek7':['NEK7','NEK7'],'AAK1':['AAK1','AAK1','KIAA1048'],'ChaK1':['ChaK1','TRPM7','CHAK1','LTRPC7'],'PYK2':['PYK2','PTK2B','FAK2','PYK2','RAFTK'],'Srm':['SRM','SRMS','C20orf148'],'LOK':['LOK','STK10','LOK'],'KHS2':['KHS2','MAP4K3','RAB8IPL1'],'OSR1':['OSR1','OXSR1','KIAA1101','OSR1'],'PAK6':['PAK6','PAK6','PAK5'],'PAK4':['PAK4','PAK4','KIAA1142'],'MST4':['MST4','MST4','MASK'],'STLK3':['STLK3','STK39','SPAK'],'STLK5':['STLK5','STRADA','LYK5','STRAD'],'STLK6':['STLK6','STRADB','ALS2CR2','ILPIP','ORF Names:','PRO1038'],'TAO3':['TAO3','TAOK3','DPK','JIK','KDS','MAP3K18'],'TAO1':['TAO1','TAOK1','KIAA1361','MAP3K16','MARKK'],'HGK/ZC1':['ZC1','HGK','MAP4K4','HGK','KIAA0687','NIK'],'TNIK/ZC2':['ZC2','TNIK','TNIK','KIAA0551'],'MINK/ZC3':['ZC3','MINK','MINK1','B55','MAP4K6','MINK','YSK2','ZC3'],'NRK/ZC4':['ZC4','NRK','NRK'],'LATS1':['LATS1','LATS1','WARTS'],'LATS2':['LATS2','LATS2','KPM'],'CDK11':['CDK11','CDK19','CDC2L6','CDK11','KIAA1028'],'NIM1':['NIM1','NIM1'],'ULK3':['ULK3','ULK3'],'CLIK1L':['CLIK1L','PDIK1L','CLIK1L'],'TTBK2':['TTBK2','TTBK2','KIAA0847'],'SCYL1':['SCYL1','SCYL1','CVAK90','GKLP','NTKL','TAPK','TEIF','TRAP','ORF Names:','HT019'],'MASTL':['MASTL','MASTL','GW','GWL','THC2'],'PINK1':['PINK1','PINK1'],'ULK4':['ULK4','ULK4'],'MLKL':['MLKL','MLKL'],'DCAMKL3':['DCAMKL3','DCLK3','DCAMKL3','DCDC3C','KIAA1765'],'SgK493':['SgK493','PKDCC','SGK493','VLK'],'PFTAIRE2':['PFTAIRE2','CDK15','ALS2CR7','PFTK2'],'STK33':['STK33','STK33'],'PRPK':['PRPK','TP53RK','C20orf64','PRPK'],'ERK7':['Erk7','MAPK15','ERK7','ERK8'],'CDKL4':['CDKL4','CDKL4'],'SCYL3':['SCYL3','SCYL3','PACE1'],'YANK3':['YANK3','STK32C'],'Nek9':['NEK9','NEK9','KIAA1995','NEK8','NERCC'],'TSSK3':['TSSK3','TSSK3','SPOGA3','STK22C'],'NuaK2':['NuaK2','NUAK2','OMPHK2','SNARK'],'RSKL2':['RSKL2','RPS6KL1'],'TSSK2':['TSSK2','TSSK2','DGSG','SPOGA2','STK22B'],'SCYL2':['SCYL2','SCYL2','CVAK104','KIAA1360'],'Nek8':['NEK8','NEK8','JCK','NEK12A'],'BARK2/GRK3':['BARK2','ADRBK2','BARK2','GRK3'],'NRBP1':['NRBP1','NRBP1','BCON3','NRBP'],'PKD2':['PKD2','PRKD2','PKD2','ORF Names:','HSPC187'],'YANK2':['YANK2','STK32B','ORF Names:','UNQ3003/PRO9744'],'CAMKK2':['CaMKK2','CAMKK2','CAMKKB','KIAA0787'],'CCRK':['CCRK','CDK20','CCRK','CDCH'],'CLK4':['CLK4','CLK4'],'CRK7':['CRK7','CDK12','CRK7','CRKRS','KIAA0904'],'DRAK1':['DRAK1','STK17A','DRAK1'],'DRAK2':['DRAK2','STK17B','DRAK2'],'DYRK3':['DYRK3','DYRK3'],'PKD3':['PKD3','PRKD3','EPK2','PRKCN'],'GCN2':['GCN2','EIF2AK4','GCN2','KIAA1338'],'SgK494':['SgK494','SGK494','SgK494'],'SgK495':['SgK495','STK40','SGK495','SHIK'],'CLIK1':['CLIK1','STK35','CLIK1','PDIK1','STK35L1'],'HH498':['HH498','TNNI3K','CARK'],'HIPK2':['HIPK2','HIPK2'],'HRI':['HRI','EIF2AK1','HRI','KIAA1369','ORF Names:','PRO1362'],'ICK':['ICK','ICK','KIAA0936'],'IRE2':['IRE2','ERN2','IRE2'],'PASK':['PASK','PASK','KIAA0135'],'NDR2':['NDR2','STK38L','KIAA0965','NDR2'],'QSK':['QSK','SIK3','KIAA0999','QSK'],'HUNK':['HUNK','HUNK','MAKV'],'MEKK6/MAP3K6':['MAP3K6','MAP3K6','ASK2','MAPKKK6','MEKK6'],'ZAK':['ZAK','MLTK','ZAK','ORF Names:','HCCS4'],'MOK':['MOK','MOK','RAGE','RAGE1'],'MPSK1':['MPSK1','STK16','MPSK1','PKL12','TSF1'],'MSSK1':['MSSK1','SRPK3','STK23','EMBL EAW72812.1','ORF Names:','hCG_39220','EMBL EAW72812.1'],'WNK1':['Wnk1','WNK1','HSN2','KDP','KIAA0344','PRKWNK1'],'CDKL3':['CDKL3','CDKL3'],'PAK5':['PAK5','PAK7','KIAA1264','PAK5'],'PKN3':['PKN3','PKN3','PKNBETA'],'QIK':['QIK','SIK2','KIAA0781','QIK','SNF1LK2'],'MARK4':['MARK4','MARK4','KIAA1860','MARKL1'],'SgK496':['SgK496','DSTYK','KIAA0472','RIP5','RIPK5','SGK496','ORF Names:','HDCMD38P'],'RSKL1':['RSKL1','RPS6KC1','RPK118'],'RSK4':['RSK4','RPS6KA6','RSK4'],'NRBP2':['NRBP2','NRBP2','ORF Names:','PP9320','TRG16'],'SgK071':['SgK071','SGK071','C9orf96'],'SGK2':['SGK2','SGK2'],'SSTK':['SSTK','TSSK6','SSTK','ORF Names:','FKSG82'],'SGK3':['SGK3','SGK3','CISK','SGKL'],'TTBK1':['TTBK1','TTBK1','BDTK','KIAA1855'],'DCAMKL2':['DCAMKL2','DCLK2','DCAMKL2','DCDC3B','DCK2'],'Slob':['Slob','PXK'],'PBK':['PBK','PBK','TOPK'],'SuRTK106':['SuRTK106','STYK1','NOK'],'TBK1':['TBK1','TBK1','NAK'],'TESK2':['TESK2','TESK2'],'Trad':['Trad','KALRN','ORF Names:','hCG_2039851','EMBL EAW79410.1'],'TSSK4':['TSSK4','TSSK4','C14orf20','STK22E','TSSK5'],'VRK3':['VRK3','VRK3'],'caMLCK':['caMLCK','MYLK3','MLCK'],'SPEG':['SPEG','SPEG','APEG1','KIAA1297'],'CK1[alpha]2':['CK1a2','CSNK1A1L'],'ANKRD3':['ANKRD3','RIPK4'],'Nek5':['NEK5','NEK5'],'CaMK1[delta]':['CaMK1d','CAMK1D','CAMKID'],'MAP3K8':['MAP3K8','MAP3K19','RCK','YSK4'],'Nek11':['NEK11','NEK11'],'GRK7':['GPRK7','GRK7','GPRK7'],'SgK069':['SgK069','SBK2','SGK069'],'HIPK4':['HIPK4','HIPK4'],'MYO3B':['MYO3B','MYO3B'],'WNK4':['Wnk4','WNK4','PRKWNK4'],'SgK110':['SgK110','SGK110'],'BRSK1':['BRSK1','BRSK1','KIAA1811','SAD1','SADB'],'Obscn':['Obscn','OBSCN','KIAA1556','KIAA1639'],'PSKH2':['PSKH2','PSKH2'],'SIK':['SIK','SIK1','SIK','SNF1LK'],'KSR2':['KSR2','KSR2'],'RIOK3':['RIOK3','RIOK3','SUDD'],'ADCK3':['ADCK3','ADCK3','CABC1','ORF Names:','PP265'],'RIOK1':['RIOK1','RIOK1'],'YANK1':['YANK1','STK32A'],'SNRK':['SNRK','SNRK','KIAA0096','SNFRK'],'EphA10':['EphA10','EPHA10'],'SgK196':['SgK196','SGK196'],'MYO3A':['MYO3A','MYO3A'],'WNK3':['Wnk3','WNK3','KIAA1566','PRKWNK3'],'SgK223':['SgK223','SGK223'],'Nek10':['NEK10','NEK10'],'EphA6':['EphA6','EPHA6','EHK2','HEK12'],'CK1[gamma]1':['CK1g1','CSNK1G1'],'SgK269':['SgK269','PEAK1','KIAA2002'],'SBK':['SBK','SBK1'],'SgK396':['SgK396','STK31','SGK396'],'SgK288':['SgK288','ANKK1','PKK2','SGK288'],'KIS':['KIS','UHMK1','KIS','KIST'],'CaMK1[beta]':['CaMK1b','PNCK'],'TBCK':['TBCK','TBCK','TBCKL','ORF Names:','HSPC302'],'SMG1':['SMG1','SMG1','ATX','KIAA0421','LIP'],'skMLCK':['skMLCK','MYLK2'],'MAP3K7':['MAP3K7','MAP3K15','ASK3'],'LRRK2':['LRRK2','LRRK2','PARK8'],'MLK4':['MLK4','MLK4','KIAA1804'],'Haspin':['Haspin','GSG2'],'Trb3':['Trb3','TRIB3','C20orf97','NIPK','SKIP3','TRB3'],'CRIK':['CRIK','CIT','CRIK','KIAA0949','STK21'],'CAMKK1':['CaMKK1','CAMKK1','CAMKKA'],'LRRK1':['LRRK1','LRRK1','KIAA1790'],'SgK307':['SgK307','TEX14','SGK307'],'MAST4':['MAST4','MAST4','KIAA0303'],'CaMK2[delta]':['CaMK2d','CAMK2D','CAMKD'],'BIKE':['BIKE','BMP2K','BIKE','ORF Names:','HRIHFB2017'],'TSSK1':['TSSK1','TSSK1B','SPOGA1','SPOGA4','STK22A','STK22D','TSSK1','ORF Names:','FKSG81'],'SgK424':['SgK424','TEX14','SGK307'],'SgK085':['SgK085','MYLK4','SGK085'],'ADCK2':['ADCK2','ADCK2','AARF'],'DAPK3':['DAPK3','DAPK3','ZIPK'],'Wee1B':['Wee1B','WEE2','WEE1B'],'RNAseL':['RNAseL','RNASEL','RNS4'],'ChaK2':['ChaK2','TRPM6','CHAK2'],'RIOK2':['RIOK2','RIOK2'],'AlphaK2':['AlphaK2','ALPK2','HAK'],'AlphaK3':['AlphaK3','ALPK1','KIAA1527','LAK'],'Brd2':['BRD2','BRD2','KIAA9001','RING3'],'Brd3':['BRD3','BRD3','KIAA0043','RING3L'],'Brd4':['BRD4','BRD4','EMBL AAH35266.1','ORF Names:','hCG_2000917','EMBL EAW84470.1'],'BrdT':['BRDT','BRDT'],'AlphaK1':['AlphaK1','ALPK3','KIAA1330','MAK'],'ADCK5':['ADCK5','ADCK5'],'TIF[alpha]':['TIF1a','TRIM24','RNF82','TIF1','TIF1A'],'TIF1[beta]':['TIF1b','TRIM28','KAP1','RNF96','TIF1B'],'TIF1[gamma]':['TIF1g','TRIM33','KIAA1113','RFG7','TIF1G'],'JAK1~b':['Domain2_JAK1','JAK1','JAK1A','JAK1B'],'JAK2~b':['Domain2_JAK2','JAK2'],'JAK3~b':['Domain2_JAK3','JAK3'],'MSK1~b':['Domain2_MSK1','RPS6KA5','MSK1'],'MSK2~b':['Domain2_MSK2','RPS6KA4','MSK2'],'RSK1~b':['Domain2_RSK1','RPS6KA2','MAPKAPK1C','RSK3'],'RSK2~b':['Domain2_RSK2','RPS6KA3','ISPK1','MAPKAPK1B','RSK2'],'RSK3~b':['Domain2_RSK3','RPS6KA1','MAPKAPK1A','RSK1'],'Tyk2~b':['Domain2_TYK2','TYK2'],'GCN2~b':['Domain2_GCN2','EIF2AK4','GCN2','KIAA1338'],'RSK4~b':['Domain2_RSK4','RPS6KA6','RSK4'],'SPEG~b':['Domain2_SPEG','SPEG','APEG1','KIAA1297'],'Obscn~b':['Domain2_Obscn','OBSCN','KIAA1556','KIAA1639']}
		SCORE=[]
		os.chdir(analysisworking)
		asd=open('Protein_list.txt','r')
		FILE1=asd.readlines()
		asd.close()
		for f in FILE1:
			if f.split('\t')[0] != 'Protein_Name':
				SCORE.append(int(f.strip('\n').split('\t')[7]))
		ONE=[]
		TWO=[]
		THREE=[]
		FOUR=[]
		FIVE=[]
		one=0
		two=0
		three=0
		four=0
		five=0
		a=1
		for f in sorted(set(sorted(SCORE)),reverse=True):
			for ff in FILE1:
				if ff.split('\t')[0] != 'Protein_Name':
					if int(ff.strip('\n').split('\t')[7]) == f:
						if a == 1:
							one=f
							ONE.append(ff.strip('\n').split('\t')[0])
						if a == 2:
							two=f
							TWO.append(ff.strip('\n').split('\t')[0])
						if a == 3:
							three=f
							THREE.append(ff.strip('\n').split('\t')[0])
						if a == 4:
							four=f
							FOUR.append(ff.strip('\n').split('\t')[0])
						if a > 4:
							FIVE.append(ff.strip('\n').split('\t')[0])
			a+=1
		five=four+1
		'''
		color codes:
		RED: 1 0 0
		BLUE: 0 0 1
		'''
		dsa=open('kinome.inp','w')
		dsa.write('scale 20\n\ncolor 1 0 0\n')
		for f in ONE:
			for ff in list(KINOME.keys()):
				for z in KINOME[ff]:
					if f == z:
						dsa.write('at '+ff+'\n'+'circle-lined'+'\n'+'text '+ff+'\n')
		if TWO:
			dsa.write('color 0 0 1\n')
			for f in TWO:
				for ff in list(KINOME.keys()):
					for z in KINOME[ff]:
						if f == z:
							dsa.write('at '+ff+'\n'+'circle-lined'+'\n'+'text '+ff+'\n')
		if THREE:
			dsa.write('color 0 0.67 0\n')
			for f in THREE:
				for ff in list(KINOME.keys()):
					for z in KINOME[ff]:
						if f == z:
							dsa.write('at '+ff+'\n'+'circle-lined'+'\n'+'text '+ff+'\n')
		if FOUR:
			dsa.write('color 1 0 1\n')
			for f in FOUR:
				for ff in list(KINOME.keys()):
					for z in KINOME[ff]:
						if f == z:
							dsa.write('at '+ff+'\n'+'circle-lined'+'\n'+'text '+ff+'\n')
		if FIVE:
			dsa.write('scale 10'+'\n'+'color 0 0 0\n')
			for f in FIVE:
				for ff in list(KINOME.keys()):
					for z in KINOME[ff]:
						if f == z:
							dsa.write('at '+ff+'\n'+'text '+ff+'\n')
		#~~ LEGEND BOX
		LEGEND="\n\nlegend\nscale 20\ntext Number of interacting criteria\nnext-line\ntext passed\nnext-line\nnext-line\ncolor 1 0 0\ncircle-lined\nspace\nspace\ntext %d\nnext-line\n" %(one)
		if TWO:
			LEGEND+="color 0 0 1\ncircle-lined\nspace\nspace\ntext %d\nnext-line\n" %(two)
		if THREE:
			LEGEND+="color 0 0.67 0\ncircle-lined\nspace\nspace\ntext %d\nnext-line\n" %(three)
		if FOUR:
			LEGEND+="color 1 0 1\ncircle-lined\nspace\nspace\ntext %d\nnext-line\n" %(four)
		if FIVE:
			LEGEND+="color 0 0 0\nspace\nspace\ntext <%d text\n" % (five)
		LEGEND+="legendBox"
		#~~~ LEGEND BOX
		dsa.write(LEGEND)
		dsa.close()
		#~~~ execute Kinome render with bash in bg
		ASD='''
		cp -r %s/postscript .
		export "PERLLIB=%s/modules"
		%s/kinome-render -i kinome.inp -o %s.ps -t2
		cd postscript; for f in `ls -1`; do rm "$f";done; cd ..;rmdir postscript
		''' %(KINOMERENDER,KINOMERENDER,KINOMERENDER,filename.split('.')[0])
		asd=open('kinome.bash','w')
		asd.write(ASD)
		asd.close()

		#~~ copy postcript templates~~~
		asd = subprocess.Popen(['bash', 'kinome.bash'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		output,error=asd.communicate()
		asd.wait()
		if error:
			print('Error occured during KinomerRender!')
		#	for f in error.split('\n'):
		#		print(f)
		for f in [ 'kinome.inp', 'kinome.bash' ]:
			os.remove(f)
		os.chdir('..')
		#~~~ Kinomerender: end
		def total_close():
			top.destroy()
			root.destroy()
		top=Toplevel(analysis_scr)
		Label(top,bg="white",text="Completed!!",font=("Arial",20,'bold'),width=20,height=3).grid(row=0,column=0,sticky=W+E+N+S)
		Button(top,bg="firebrick1",fg="white",text="Press Here \nto quit",relief=RAISED,borderwidth=3,font=("Arial",15,'bold'),width=20,height=3,command=total_close).grid(row=1,column=0,sticky=W+E+N+S)
	#~~~~~~~ File Input ~~~~~~
	def askfile():
		global filename 
		global filedir
		filen= tkinter.filedialog.askopenfilename(initialdir="~",title="Select File",filetypes=(("text files","*.txt"),("all files","*.*")))
		if filen :
			if os.path.exists(filen):
				filedir,filename=os.path.split(filen)
		else:
			tkinter.messagebox.showinfo("Warning!", "File not specified", parent=analysis_scr)
			return	
	#~~~ Region with number
	def reference_num():
		refrence=Toplevel(analysis_scr)
		Label(refrence,bg="white",text="ATP Binding\nsite Region",font=("Arial",10,'bold'),relief=SOLID,width=15,height=2).grid(row=0,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="Binding Pocket",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=0,column=1,sticky=W+E+N+S)
		Label(refrence,bg="yellow",text="I",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=1,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="1,2,3",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=1,column=1,sticky=W+E+N+S)
		Label(refrence,bg="lawngreen",text="g.l",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=2,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="4,5,6,7,8,9",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=2,column=1,sticky=W+E+N+S)
		Label(refrence,bg="yellow",text="II",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=3,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="10,11,12,13",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=3,column=1,sticky=W+E+N+S)
		Label(refrence,bg="yellow",text="III",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=4,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="14,15,16,17,18,19",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=4,column=1,sticky=W+E+N+S)
		Label(refrence,bg="red",text="aC",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=5,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="20,21,22,23,24,25,26,27,28,29,30",font=("Arial",10,'bold'),relief=SOLID,width=34,height=1).grid(row=5,column=1,sticky=W+E+N+S)
		Label(refrence,bg="lawngreen",text="b.l",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=6,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="31,32,33,34,35,36,37",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=6,column=1,sticky=W+E+N+S)
		Label(refrence,bg="yellow",text="IV",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=7,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="38,39,40,41",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=7,column=1,sticky=W+E+N+S)
		Label(refrence,bg="yellow",text="V",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=8,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="42,43,44",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=8,column=1,sticky=W+E+N+S)
		Label(refrence,bg="yellow",text="GK",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=9,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="45",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=9,column=1,sticky=W+E+N+S)
		Label(refrence,bg="purple",fg="white",text="HINGE",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=10,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="46,47,48",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=10,column=1,sticky=W+E+N+S)
		Label(refrence,bg="lightblue1",text="linker",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=11,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="49,50,51,52",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=11,column=1,sticky=W+E+N+S)
		Label(refrence,bg="red",text="aD",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=12,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="53,54,55,56,57,58,59",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=12,column=1,sticky=W+E+N+S)
		Label(refrence,bg="red",text="aE",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=13,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="60,61,62,63,64",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=13,column=1,sticky=W+E+N+S)
		Label(refrence,bg="yellow",text="VI",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=14,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="65,66,67",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=14,column=1,sticky=W+E+N+S)
		Label(refrence,bg="orange",text="c.l",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=15,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="68,69,70,71,72,73,74,75",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=15,column=1,sticky=W+E+N+S)
		Label(refrence,bg="yellow",text="VII",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=16,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="76,77,78",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=16,column=1,sticky=W+E+N+S)
		Label(refrence,bg="yellow",text="VIII",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=17,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="79",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=17,column=1,sticky=W+E+N+S)
		Label(refrence,bg="cornflower blue",text="xDFG",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=18,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="80,81,82,83",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=18,column=1,sticky=W+E+N+S)
		Label(refrence,bg="cornflower blue",text="a.l",relief=SOLID,font=("Arial",10,'bold'),width=10,height=1).grid(row=19,column=0,sticky=W+E+N+S)
		Label(refrence,bg="white",text="84,85",font=("Arial",10,'bold'),relief=SOLID,width=28,height=1).grid(row=19,column=1,sticky=W+E+N+S)
	reference_num()
	def reanalysis():
		global analysisworking
		Analysiscount=1
		filen= tkinter.filedialog.askopenfilename(initialdir="/home/bioinfo/Desktop/sam/KLIFS_database/Reverse_screening/gui",title="Select File",filetypes=(("txt files","*.txt"),("all files","*.*")))
		if filen :
			if os.path.exists(filen):
				filedir,filename=os.path.split(filen)
		else:
			tkinter.messagebox.showinfo("Warning!", "File not specified", parent=analysis_scr)
			return
		#~~~~ Check for Files and other input ~~~~
		if not filename:
			tkinter.messagebox.showinfo("Warning","Please provide the input file!")
			return
		#~~~~ Check for Files and other input ~~~~
		os.chdir(filedir)
		#~~~ check if any other analysis dir present or not
		analysisdir=os.listdir('.')
		qwerty=[]
		analysiscountcheck="NO"
		for f in analysisdir:
			if re.match("Reanalysis_",f):
				analysiscountcheck="YES"
		if analysiscountcheck == "YES":
			for f in analysisdir:
				if re.match("Reanalysis_",f):
					qwerty.append(f.strip('\n'))
			Analysiscount=int(max(qwerty).split('_')[1])+1
		os.mkdir('Reanalysis_'+str(Analysiscount)) #Analysiscount
		os.chdir('Reanalysis_'+str(Analysiscount))
		analysisworking=filedir+'/Reanalysis_'+str(Analysiscount)
		asd=open('../'+filename,'r')
		FILE1=asd.readlines()
		asd.close()
		SINGLE_REP={}
		SINGLE_REP_INT={}
		LIST_STR_SORT={}
		GENE={}
		GENE_INT={}
		option_len=0
		for f in FILE1:
			if f.split('\t')[0] != 'Struct_Name':
				option_len=len(f.split('\t')[9:])
				SINGLE_REP[f.split('\t')[0]]=[]
				SINGLE_REP_INT[f.split('\t')[0]]=[]
				GENE[f.split('\t')[0].split('_')[0]]=[]
				GENE_INT[f.split('\t')[0].split('_')[0]]=[]

		for f in FILE1:
			temp=[]
			if f.split('\t')[0] != 'Struct_Name':
				temp.append(f.split('\t')[0]);temp.append(int(f.split('\t')[1]));temp.append(f.split('\t')[2]);temp.append(f.split('\t')[3]);temp.append(f.split('\t')[4]);temp.append(f.split('\t')[5]);temp.append(float(f.split('\t')[6]));temp.append(int(f.split('\t')[7])); temp.append(int(f.split('\t')[8]))
				for z in f.split('\t')[9:]:
					temp.append(z.strip('\n'))
				SINGLE_REP[f.split('\t')[0]].append(temp)
				SINGLE_REP_INT[f.split('\t')[0]].append(int(f.split('\t')[8]))
				LIST_STR_SORT[int(f.split('\t')[8])]=[]

		GENE_OUT={}
		#~~~~~ Best single rep from rest poses
		for z in SINGLE_REP.keys():
			highest_int=max(SINGLE_REP_INT[z])
			best_int_from_pose=[]
			for f in SINGLE_REP[z]:
				if f[8] == highest_int:
					best_int_from_pose.append(f)
			for f in sorted(best_int_from_pose, key =lambda x:(x[6],-x[7])):
				LIST_STR_SORT[f[8]].append(f)
				GENE[f[0].split('_')[0]].append(f)
				GENE_INT[f[0].split('_')[0]].append(f[8])
				GENE_OUT[f[8]]=[]
				break
		asd=open('Best_pose_structure.txt','w')
		ghj='Struct_Name\tPose_Num\tFamily\tMutation\tDFG\taC\tEnergy\tTotal_Int\tInt_pattern'
		for a in range(1,option_len+1):
			ghj+='\t'+'Option_'+str(a)
		asd.write(ghj+'\n')
		for z in sorted(LIST_STR_SORT.keys(),reverse=True):
			for f in sorted(LIST_STR_SORT[z],key= lambda x:(x[6],-x[7])):
				temp=f[0]
				for r in f[1:]:
					temp+='\t'+str(r)
				asd.write(temp+'\n')
		asd.close()
		#~~~~~ Gene from rest structures
		asd=open('Protein_list.txt','w')
		ghj='Protein_Name\tFamily\tMutation\tDFG\taC\tEnergy\tTotal_Int\tInt_pattern'
		for a in range(1,option_len+1):
			ghj+='\t'+'Option_'+str(a)
		asd.write(ghj+'\n')
		for z in GENE.keys():
			highest_int=max(GENE_INT[z])
			best_gene=[]
			for f in GENE[z]:
				if f[8] == highest_int:
					best_gene.append(f)
			for f in sorted(best_gene, key = lambda x : (x[6],-x[7])):
				GENE_OUT[f[8]].append(f)
				break
		for z in sorted(GENE_OUT.keys(),reverse=True):
			for f in sorted(GENE_OUT[z], key = lambda x:(x[6],-x[7])):
				temp=f[0].split('_')[0]
				for r in f[2:]:
					temp+='\t'+str(r)
				asd.write(temp+'\n')
		asd.close()
		Analysiscount+=1
		run_kinomerender(filename)
			
	#~~ File Input
	Label(analysis_scr,bg="white",text="File Input --->",font=("Arial",15,'bold'),width=25,height=2).grid(row=0,column=0,columnspan=2,sticky=W+E+N+S)
	Button(analysis_scr,bg="white",text="Open..",relief=RAISED,borderwidth=3,font=("Arial",15,'bold'),width=25,height=2,command=askfile).grid(row=0,column=2,columnspan=2,sticky=W+E+N+S)
	Button(analysis_scr,bg="white",text="Reanalysis\nOpen..",relief=RAISED,borderwidth=3,font=("Arial",12,'bold'),width=5,height=2,command=reanalysis).grid(row=0,column=4,sticky=W+E+N+S)	# Reanalysis
	#~~~ File Input
	Button(analysis_scr,bg="yellow",text="I",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_I).grid(row=1,column=0,sticky=W+E+N+S)
	Button(analysis_scr,bg="lawngreen",text="g.l",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_gl).grid(row=1,column=1,sticky=W+E+N+S)
	Button(analysis_scr,bg="yellow",text="II",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_II).grid(row=1,column=2,sticky=W+E+N+S)
	Button(analysis_scr,bg="yellow",text="III",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_III).grid(row=1,column=3,sticky=W+E+N+S)
	Button(analysis_scr,bg="red",text="aC",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_aC).grid(row=1,column=4,sticky=W+E+N+S)
	Button(analysis_scr,bg="lawngreen",text="b.l",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_bl).grid(row=2,column=0,sticky=W+E+N+S)
	Button(analysis_scr,bg="yellow",text="IV",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_IV).grid(row=2,column=1,sticky=W+E+N+S)
	Button(analysis_scr,bg="yellow",text="V",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_V).grid(row=2,column=2,sticky=W+E+N+S)
	Button(analysis_scr,bg="yellow",text="GK",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_GK).grid(row=2,column=3,sticky=W+E+N+S)
	Button(analysis_scr,bg="purple",fg="white",text="HINGE",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_hinge).grid(row=2,column=4,sticky=W+E+N+S)
	Button(analysis_scr,bg="lightblue1",text="linker",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_linker).grid(row=3,column=0,sticky=W+E+N+S)
	Button(analysis_scr,bg="red",text="aD",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_aD).grid(row=3,column=1,sticky=W+E+N+S)
	Button(analysis_scr,bg="red",text="aE",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_aE).grid(row=3,column=2,sticky=W+E+N+S)
	Button(analysis_scr,bg="yellow",text="VI",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_VI).grid(row=3,column=3,sticky=W+E+N+S)
	Button(analysis_scr,bg="orange",text="c.l",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_cl).grid(row=3,column=4,sticky=W+E+N+S)
	Button(analysis_scr,bg="yellow",text="VII",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_VII).grid(row=4,column=0,sticky=W+E+N+S)
	Button(analysis_scr,bg="yellow",text="VIII",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_VIII).grid(row=4,column=1,sticky=W+E+N+S)
	Button(analysis_scr,bg="cornflower blue",text="xDFG",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_xDFG).grid(row=4,column=2,sticky=W+E+N+S)
	Button(analysis_scr,bg="cornflower blue",text="a.l",relief=RAISED,borderwidth=3,font=("Arial",25,'bold'),width=5,height=2,command=fun_al).grid(row=4,column=3,sticky=W+E+N+S)
	Button(analysis_scr,bg="black",fg="white",text="HIT RUN!",relief=RAISED,borderwidth=3,font=("Arial",15,'bold'),width=5,height=2,command=run_analysis_calc).grid(row=4,column=4,sticky=W+E+N+S)

#~~~~ End of Run analysis~~~~~~~~~~~~~~~~~
#~~~ Start of Main window ~~~~
Label(root,bg="white",text="KinomeRun",font=("Arial New Roman",30,'bold'),width=30,height=3).grid(row=0,column=0,columnspan=6,sticky=W+E+N+S)
PARALLEL_check=IntVar()
VINA_check=IntVar()
KIN_check=IntVar()
PLIP_check=IntVar()
KINDB_check=IntVar()
def software_check():
	if PARALLEL_check.get() == 0:
		tkinter.messagebox.showinfo("Warning!", "GNU Pallel not found!\nPlease Install GNU Parallel.", parent=root)
		return	
	if VINA_check.get() == 0:
		tkinter.messagebox.showinfo("Warning!", "AutoDock Vina not found!\nPlease Install AutoDock Vina.", parent=root)
		return

Label(root,bg="white",text="Softwares:",font=("Arial",10,'bold'),relief=SOLID,width=10,height=3).grid(row=1,column=0,sticky=W+E+N+S)
#~~ GNU Parallel
asd=subprocess.Popen(['command -v parallel'],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
output,error=asd.communicate()
asd.wait()
if output:
	PARALLEL_check.set(1)
else:
	PARALLEL_check.set(0)
Checkbutton(root,variable=PARALLEL_check,text="GNU Parallel",state=DISABLED,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=1,sticky=W+E+N+S)
#~~~
#~~~ Vina
asd=subprocess.Popen(['command -v vina'],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
output,error=asd.communicate()
asd.wait()
if output:
	VINA_check.set(1)
else:
	VINA_check.set(0)
Checkbutton(root,variable=VINA_check,text="AutoDock Vina",state=DISABLED,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=2,sticky=W+E+N+S)
#~~~~~~~~
#~~~~~~~~~~~ CONFIG FILE ~~~~~~
CONFIG_check=IntVar()

asd_config = configparser.ConfigParser()
asd_config.optionxform = lambda option: option
if os.path.isfile("config.ini"):
	asd_config.read("config.ini")
	for a, b in asd_config.items("softwares"):
		if a == "KINOMERENDER":
			KINOMERENDER = b
		if a == "PLIP":
			PLIP = b
		if a == 'KINASE_DB':
			KINASE_DB = b
#	if KINOMERENDER and PLIP:
#		CONFIG_check.set(1)
#	else:
#		CONFIG_check.set(0)
#else:
#	CONFIG_check.set(0)
def config_writer(TOOLNAME,PATH):
	dsa_config=configparser.ConfigParser()
	dsa_config.optionxform = lambda option: option
	if dsa_config.read('config.ini'):
		pass
	else:
		dsa_config.add_section("softwares")
	dsa_config.set("softwares",TOOLNAME,PATH)
	config_file=open('config.ini','w')
	dsa_config.write(config_file)
	config_file.close()
	dsa_config=''

#~~~ Kinome-Render
def get_kinome_dir():
	KIN_check.set(0)
	global KINOMERENDER
	filen = tkinter.filedialog.askdirectory(initialdir="~", title="Select Kinome Render Directory", parent=root)
	if filen:
		# ~~~~~ Check for correct KinomeRender Directory or not ~~~~~~~~
		if ' ' in filen:
			tkinter.messagebox.showinfo("Warning!", "Whitespace found in the specified directory!\nKindly remove the whitespace in directoy naming", parent=root)
			return
		else:
			if os.path.isdir(filen):
				if os.path.isfile(filen + "/kinome-render"):
					KINOMERENDER=filen
					config_writer('KINOMERENDER',KINOMERENDER)
					KIN_check.set(1)
				else:
					tkinter.messagebox.showinfo("Warning!", "Kinome-render exe not found in the specified directory!", parent=root)
					return
	else:
		tkinter.messagebox.showinfo("Warning!", "File directory not specified!", parent=root)
		return	

def kinome_check(*args):
	if KIN_check.get() == 1:
		Checkbutton(root,variable=KIN_check,text="Kinome Render",state=DISABLED,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
KIN_check.trace('w',kinome_check)

if KINOMERENDER:
	KIN_check.set(1)
	Checkbutton(root,variable=KIN_check,text="Kinome Render",state=DISABLED,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=3,sticky=W+E+N+S)
else:
	KIN_check.set(0)
	Button(root,text="Kinome Render",bg="white",width=7,height=3,relief=RAISED,borderwidth=3,command=get_kinome_dir).grid(row=1,column=3,sticky=W+E+N+S)
#~~~~
#~~~~ PLIP
def get_plip_dir():
	global PLIP
	PLIP_check.set(0)
	filen = tkinter.filedialog.askdirectory(initialdir="~", title="Select PLIP Directory")
	if filen:
		if ' ' in filen:
			tkinter.messagebox.showinfo("Warning!", "Whitespace found in the specified directory!\nKindly remove the whitespace in directoy naming", parent=root)
			return
		else:
			# ~~~~~ Check for correct plip Directory or not ~~~~~~~~
			if os.path.isdir(filen):
				if os.path.isfile(filen + "/plipcmd") or os.path.isfile(filen + "/plipcmd.py"):
					PLIP=filen
					config_writer('PLIP',PLIP)
					PLIP_check.set(1)
				else:
					tkinter.messagebox.showinfo("Warning!", "plipcmd not found in the specified directory!", parent=root)
					return
	else:
		tkinter.messagebox.showinfo("Warning!", "File directory not specified!", parent=root)
		return	

def plip_check(*args):
	if PLIP_check.get() == 1:
		Checkbutton(root,variable=PLIP_check,text="PLIP",state=DISABLED,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
PLIP_check.trace('w',plip_check)

if PLIP:
	PLIP_check.set(1)
	Checkbutton(root,variable=PLIP_check,text="PLIP",state=DISABLED,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=4,sticky=W+E+N+S)
else:
	PLIP_check.set(0)
	Button(root,text="PLIP",bg="white",width=7,height=3,relief=RAISED,borderwidth=3,command=get_plip_dir).grid(row=1,column=4,sticky=W+E+N+S)
#~~~~
#~~~ KinaseDB dir
def get_kindb_dir():
	global KINASE_DB
	KINDB_check.set(0)
	filen = tkinter.filedialog.askdirectory(initialdir="~", title="Select Kinome Dataset Directory")
	if filen:
		if ' ' in filen:
			tkinter.messagebox.showinfo("Warning!", "Whitespace found in the specified directory!\nKindly remove the whitespace in directoy naming", parent=root)
			return
		else:
			# ~~~~~ Check for correct KinaseDB Directory or not ~~~~~~~~
			if os.path.isdir(filen):
				if os.path.isfile(filen + "/Pocket_index.txt"):
					KINASE_DB=filen
					config_writer('KINASE_DB',KINASE_DB)
					KINDB_check.set(1)
				else:
					tkinter.messagebox.showinfo("Warning!", "plipcmd not found in the specified directory!", parent=root)
					return
	else:
		tkinter.messagebox.showinfo("Warning!", "File directory not specified!", parent=root)
		return	

def kindb_check(*args):
	if KINDB_check.get() == 1:
		Checkbutton(root,variable=KINDB_check,text="KinaseDB",state=DISABLED,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
KINDB_check.trace('w',kindb_check)


if KINASE_DB:
	KINDB_check.set(1)
	Checkbutton(root,variable=KINDB_check,text="KinaseDB",state=DISABLED,bg="white",width=7,height=3,relief=SOLID).grid(row=1,column=5,sticky=W+E+N+S)
else:
	KINDB_check.set(0)
	Button(root,text="KinaseDB",bg="white",width=7,height=3,relief=RAISED,borderwidth=3,command=get_kindb_dir).grid(row=1,column=5,sticky=W+E+N+S)
#~~~~~~~~~~~~~
Button(root, bg="chocolate1", text="Run Screening", relief=RAISED, borderwidth=3, font=("Arial",20,'bold'), width=10, height=3, command=run_screening).grid(row=2, column=0, columnspan=3, sticky=W+E+N+S)
Button(root, bg="deep pink", text="Run Analysis", relief=RAISED, borderwidth=3, font=("Arial", 20, 'bold'), width=10, height=3, command=run_analysis).grid(row=2, column=3, columnspan=3, sticky=W+E+N+S)
mainloop()
