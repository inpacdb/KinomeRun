#!/bin/bash
if [ "$#" == 0 ]; then echo -e "No input given!\nCheck the help for providing the inputs.\n";exit;fi
while [ "$#" -gt 0 ]
do 
	case "$1"
	in
		-l)	#Ligand directory
			if [ -d "$2" ]; then totlig=$( ls -1U "$2" | grep 'pdbqt' | wc -l); if [ "$totlig" -eq 0 ]; then echo -e "No ligand found in the "$LIGAND" directory!\nPlease check the directory path."; exit; fi; fi
			LIGAND="$2"
			shift
			;;
		-d)	# Kinome dataset directory
			#Check for the receptor and config files and pocket index etc.,
			if [ -e "$2"/xmltree_KLIFS.py ]; then : ; else echo -e "Kindly provide the correct kinomedataset directory!" ; exit;fi
			KINASE_DB="$2"
			shift
			;;
		-p)	#PLIP directory
			if [ -e "$2"/plip/plipcmd.py ];then : ; else echo -e "Wrong PLIP directory specified.";exit;fi	# check for PLIP directory
			PLIP="$2"/plip
			shift
			;;
		-w)	#working directory
			if [ -d "$2" ]; then	if [ $(ls -1U "$2" | wc -l) -ne 0 ]; then echo -e "The specified working directory "$WORKING" is not empty!\nKindly Check it."; exit;	fi; fi
			WORKING="$2"
			shift
			;;		
		-h)	echo -n "
KinomeRun - Command line version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-h To print help file
-l To specify ligand directory 
-d To speficy the directory containing kinome dataset
-p To specify the directory containing PLIP 
-w To specify the working directory
-x To specify the exhaustiveness
-c To specify number of jobs for running single Vina job
-j To specify the total number of CPUs to use
-hpc For running jobs in hpc"
			exit
			;;
		-x)	#exhaustiveness
			ex="$2"
			shift
			;;
		-c)	#No. of jobs for single vina job
			numcpu="$2"
			shift
			;;
		-j)	#Total number of jobs
			jtemp="$2"
			shift
			;;
		-hpc)	#HPC
			HPC="YES"
			;;
		*)	echo -e "Wrong input given. Try it again."
			exit
			;;
	esac
	shift
done
#~~~~~~ Check for variables
if [ -z "$LIGAND" ];then echo -e "Error: The Ligand directory is not specified in the input!";exit;fi
if [ -z "$WORKING" ];then echo -e "Error: The Working directory is not specified in the input!";exit;fi
if [ -z "$KINASE_DB" ];then echo -e "Error: The KinomeDB directory is not specified in the input!";exit;fi
if [ -z "$PLIP" ];then echo -e "Error: The PLIP directory is not specified in the input!";exit;fi
if [ -z "$ex" ]; then echo -e "Error: Exhaustiveness is not specified in the input!"; exit;fi
if [ -z "$numcpu" ];then echo -e "Error: The number of jobs for each vina job is not specified!";exit;fi
if [ -z "$jtemp" ];then echo -e "Error: The total number of jobs for running in parallel is not specified!";exit;fi
if [ -z "$HPC" ]; then HPC="NO"; fi
#joobs
joobs=$( echo -e ""$jtemp"\t"$numcpu"" | awk '{s=$1/$2} {printf "%d", s}')

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

echo -e "KinomeRun - Virtual screening Module:"
echo -e "==============================================================================="
echo " Ligand directory: "$LIGAND""
echo " Protein directory: "$KINASE_DB"/receptor"
echo " Working directory: "$WORKING""
echo " Exhaustiveness: "$ex""
echo " Number of CPU for running one Vina job: "$numcpu""
echo -e " Number of VINA jobs to run in parallel: "$joobs""
echo -e " HPC run: "$HPC""
echo -e "===============================================================================\n"
echo -e "Enter\n[1] To accept these parameters\n[2] To exit"
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
echo -e "\n-------------------------------------------------------------------------------\n---------------------------------Summary Report--------------------------------\n-------------------------------------------------------------------------------\nLigand Input Directory="$LIGAND"\nReceptor Input Directory="$KINASE_DB"/receptor\nWorking directory="$WORKING"\nThe number of ligand complex needed to be generated after VS:"$top"\n" >>"$WORKING"/summary.txt
## Space check and file renaming##
cd "$LIGAND"; ls -1 | grep 'pdbqt' >spacecheck.txt
spacecheck=`sed -n "/\s/p" spacecheck.txt`
if [ -n "$spacecheck" ]
then
	echo -e "~~Space detected in the ligand files~~~\nSpace will be replaced by _ in the filename"
	sed -n "/\s/p" spacecheck.txt >spacefiles.txt
	echo -n "
	#!/bin/bash
	bspace=\`echo \"\$1\" | sed \"s/\s/_/g\"\` 
	mv \"\$1\" \"\$bspace\"" >rename.bash
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
	if f[0:6].strip() in [ 'ATOM', 'HETATM' ]:
		print(f[17:20].strip())
		break" >"$WORKING"/"$l"/docked_files/plip_temp/ligname.py
	echo -n "
	#!/bin/bash
	cd plip_temp; mkdir \${1%.pdbqt}; cd \${1%.pdbqt}
	while read -r ll
	do
		echo \"\$ll\" >>temp.pdbqt
		if [ \"\$ll\" == 'ENDMDL' ]
		then
			LIGNAME=\$(python ../ligname.py temp.pdbqt)
			cut -c-66 ../../\"\$1\" >\${1%.pdbqt}.pdb;
			sed '/ROOT/d;/ENDROOT/d;/BRANCH/d;/ENDBRANCH/d;/TORSDOF/d' temp.pdbqt | cut -c-66 >>\${1%.pdbqt}.pdb
			"$PLIP"/plipcmd.py -f \${1%.pdbqt}.pdb -x --name \${1%.pdbqt}
			python "$KINASE_DB"/xmltree_KLIFS.py \${1%.pdbqt}.xml \$(grep 'MODEL' temp.pdbqt| awk '{print \$2}') \$(grep 'RESULT' temp.pdbqt| awk '{print \$4}') \"\$LIGNAME\" "$KINASE_DB" >>../../../Results/\"\$2\".txt
			rm *.pdb temp.pdbqt \${1%.pdbqt}.xml
		fi
	done <../../pdbqt_out/\"\$1\"
	cd ..; rmdir \${1%.pdbqt}" >"$WORKING"/"$l"/docked_files/plip_temp/plip.bash
	echo -e ""$l" file created and respective protein and configuration file moved\n\n"
	echo -e "Ligand "$l" is in the "$l" directory\n" >>"$WORKING"/summary.txt	
	clear
done <ligand_list.txt
####Virutal screnning###
cd "$LIGAND"
time=`date +"%c"`; echo -e "Virtual screening start time : "$time"\n" >>"$WORKING"/summary.txt
while read -r l
do
	echo -e " ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	echo -e " + KinomeRun - Virtual screening:                                           +"
	echo -e " + -----------------------------                                            +"
	echo -e " + Multiple protein Virtual screening using Autodock Vina: Running...       +"
	echo -e " + 	* Parallel Docking            : Running...                          +"
	echo -e " ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	echo -e "\n"
	cd "$KINASE_DB"/receptor
	echo -e "~~~~~Running Autodock Vina virtual screening for "$l"~~~~~~\n\n"
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
time=`date +"%c"`; echo -e "Virtual screening end time : "$time"\n" >>"$WORKING"/summary.txt
echo "
If you used ReverseKinase in your work, please cite: 

Samdani, A. and Vetrivel, U. (2018)." >>"$WORKING"/summary.txt
