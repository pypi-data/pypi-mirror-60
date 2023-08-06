#!/bin/bash

# ===================================================================
# arancini 0.1.0 || sc-ATAC/RNA utils package
# ===================================================================

# ===================================================================
# Command line usage: arancini trimqc --input --output
# ===================================================================

package=arancini

# command line argument parsing
while test $# -gt 0; do
  case "$1" in
    -h|--help)
      echo "$package - Version 0.1.0: scATAC-seq pre-processing"
      echo " "
      echo "$package -i [input_dir] -o [output_dir]"
      echo " "
      echo "options:"
      echo "-h, --help                display help menu"
      echo "-i, --input=DIR           specify a directory containing all fastqs you wish to be processed"
      echo "-g, --genome=DIR          specify a directory the desired index reference genome"
      echo "-o, --output-dir=DIR      specify a directory to store output in"
      exit 0
      ;;
    -i | --input)
      shift
      if test $# -gt 0; then
        # user supplies a path, it searches for all fastqs within that path
        export fastqs=$(ls -LR ${1})
      else
        echo "no input fastqs specified"
        exit 1
      fi
      shift
      ;;
    -b | --barcode_sig)
      shift
      if test $# -gt 0; then
        # user supplies a path, it searches for all fastqs within that path
        export barcode_sig=${1}
      else
        echo "Add something that makes your barcode stand out relative to the rest of the raw reads so arancini can grab the fastq with the barcode reads"
        echo "Example: **/*R2_001.fixed.fastq*"
        exit 1
      fi
      shift
      ;;
    -g | --genome)
      shift
      if test $# -gt 0; then
        # user supplies a path, it searches for all fastqs within that path
        export ref=${1}
      else
        echo "no reference genome specified"
        exit 1
      fi
      shift
      ;;
    -p | --peaks)
      shift
      if test $# -gt 0; then
        # user supplies a path to a bed file of peaks or bins
        export binpeak=${1}
      else
        echo "a bed file containing peaks or bins is required to make count matrices"
        exit 1
      fi
      shift
      ;;
    -f | --binfile)
      shift
      if test $# -gt 0; then
        # user supplies a path to a bed file of peaks or bins
        export binbed=${1}
      else
        echo "Provide a peaks or bin file"
        echo "Note: peak calling is not yet supported but coming soon."
        exit 1
      fi
      shift
      ;;
    -o | --output)
      shift
      if test $# -gt 0; then
        export outs=$1
      else
        echo "no output dir specified"
        exit 1
      fi
      shift
      ;;
    *)
      break
      ;;
  esac
done

# ===========================================================================
# build the '.preprocessing/outs/' directory tree
# ===========================================================================

# specify bulk of output directories
preprocessing=./preprocessing/
trimmed_reads=${preprocessing}/trimmed_reads
paired_reads=${trimmed_reads}/${gen_struct}/paired
unpaired_reads=${trimmed_reads}/${gen_struct}/unpaired
barcode_reads=${preprocessing}/barcodes/
alignment=${preprocessing}/alignment
all_aligned=$alignment/*
tmp=${preprocessing}/tmp

# specify QC directories
qcreports=${preprocessing}/qc_reports
rawqc=${qcreports}/raw
trimqc=${qcreports}/trimmed_read_qc
qc_aggr=${qcreports}/qc_aggregate

# out dirs
counts=${outs}/count_matrices
binfiles=${tmp}/${binfiles}
# sc bams dirs are defined below in a looped function

# make directories
if test -d $preprocessing
then
    echo "$preprocessing exists"
else
  echo "Making preprocessing output directories..."
  mkdir ${preprocessing}
  mkdir ${trimmed_reads}
  mkdir ${paired_reads}
  mkdir ${unpaired_reads}
  mkdir ${alignment}
  mkdir ${tmp}
  mkdir ${qcreports}
  mkdir ${rawqc}
  mkdir ${trimqc}
  mkdir ${qc_aggr}
  mkdir ${outs}
  mkdir ${barcodes}
  mkdir ${counts}
  mkdir ${binfiles}
fi

# ===========================================================================
# quality checking and read trimming
# ===========================================================================

# loop through files for pre-trimming FastQC
for file in ${fastqs}
do
  echo ${file}
  fastqc ${file} -o ${rawqc}
  echo "fastqc has finished for the file: ${file}"
done

# list all relevant SRR indices and grab access to files
forward_read_path=$(ls ${fastqs}_1.fastq.gz)
reverse_read_path=$(ls ${fastqs}_2.fastq.gz)

for sample in ${forward_read_path}
do
  echo ${sample} >> $intermediatefiles/forward_reads
done

for sample in ${reverse_read_path}
do
  echo ${sample} >> ${tmp}/reverse_reads
done

paste -d '\t' ${tmp}/forward_reads ${tmp}/reverse_reads > ${tmp}/labelled_reads

# trim reads
while read -r line
do
  x=$(echo ${line} | awk '{ print $1 }')
  y=$(echo ${line} | awk '{ print $2 }')
  a=${x:41:10} # forward
  b=${y:41:10} # reverse
  trimmomatic PE -threads 10 ${x} ${y} ${paired_reads}/for_paired_"$a".fastq.gz ${unpaired_reads}/for_unpaired_"${a}".fastq.gz ${paired_reads}/rev_paired_"${b}".fastq.gz ${unpaired_reads}/rev_unpaired_"${b}".fastq.gz LEADING:3 TRAILING:3 SLIDINGWINDOW:4:15 MINLEN:36
  echo "trimmomatic is complete for ${a} and ${b}"
done < ${tmp}/labelled_reads

# loop through the trimmed FASTQ files for post-trimming FastQC
for file in ${fastqs}
do
  echo ${file}
  fastqc ${file} -o ${trimqc}
  echo "fastqc has finished for the file: ${file}"
done

# perform multiQC to aggregate the QC results across all of the previously generated .html files from the FASTQC runs
multiqc $fastqs -o $qc_aggr
multiqc $paired_reads/* -o $qc_aggr

# ===========================================================================
# raw read formatting and bwa alignment
# ===========================================================================

# get the list of SRR samples # trimmed samples
samplelist=$(ls ${paired_reads})

for sample in ${samplelist}
do
  inpath=${paired_reads}
  outpath=${alignment}/${sample}
  # mkdir ${outpath}

  forout=${inpath}/for_paired_${sample}.fixed.fastq.gz
  revout=${inpath}/rev_paired_${sample}.fixed.fastq.gz

  # reformat reads such that they are ammenable to BWA
  zcat ${inpath}/for_paired_${sample}.fastq | sed -E "s/^((@|\+)SRR[^.]+\.[^.]+)\.(1|2)/\1/" > ${forout}
  zcat ${inpath}/rev_paired_${sample}.fastq | sed -E "s/^((@|\+)SRR[^.]+\.[^.]+)\.(1|2)/\1/" > ${revout}

  # bwa-mem
  bwa mem -M -t 24 ${ref} ${forout} ${revout} > $outpath/${sample}.aln.sam
done


# ===========================================================================
# execute bam_tag.py - adds CB, UMI, and polyT tags to bam file
# ===========================================================================

python bam_tag.py ${all_aligned} ${barcodes} ${barcode_sig}

# ===========================================================================
# sort and split by cell barcode then sort and deduplicate
# ===========================================================================

files=$(ls ${alignment})

for f in ${files}
do

  base=${f:72:10}
  echo ${base}
  sortedbam=${out}/${base}/${base}.sort.bam
  cbsortedbam=${out}/${base}/${base}.cbsort.bam

  # sort by cell barcode with samtools
  echo "Sorting bam by cell barcode..."
  samtools sort -t CB -@ 20 ${f}  > ${cbsortedbam}

  # call python script to split the bam file by the corresponding barcodes
  echo "Spliting bulk bam by cell barcode..."
  python cb_split.py ${base}
  echo "Finished splitting ${base} into single cell files"

  cb_split_out=${outs}/sc-bams/${base}/notdedup/*
  scbams=$(ls ${cb_split_out})
  sorted_out=${outs}/sc-bams/${base}/possorted_scbams
  dedup_out=${outs}/sc-bams/${base}/deduplicated_scbams/
  percell=${outs}/sc-bams/${base}/

  if test -d ${sorted_out}
  then
      echo "${sorted_out} exists"
  else
    echo "Making directory: ${sorted_out}"
    mkdir ${sorted_out}
  fi

  # loop through the folder of sc-bams for the current sample
  for scbam in ${scbams}
  do
    cell=${scbam:103:12}
    samtools sort ${scbam} > ${sorted_out}/${cell}.sort.bam
    # index each single cell bam with samtools
    echo "Indexing the bam..."
    samtools index ${sorted_out}/${cell}.sort.bam

    # dedup each sc-bam with umi tools
    dedupbam=${dedupout}/${cell}.possort.dedup.bam
    echo "Deduplicating the bam with UMI tools..."
    umi_tools dedup -I ${sorted_out}/${cell}.sort.bam --cell-tag="CB" --extract-umi-method=tag --umi-tag="UM" --output-stats=deduplicated -S ${dedupbam}
    mv ./*.tsv ${percell}
    # -L ${percell} -E ${percell} doesn't work for some reason to move the .tsv files
  done
  # now we have the final dedup and sorted single cell bams! useful for many tools

  # get read coverage
  dirlist=(`ls ${dedupout}/*.bam`)

  for FILE in ${dirlist[*]}
  do
  	CELL=$(echo $(basename $FILE) | awk -F "." '{print $1}')
  	echo $CELL
      bedtools coverage -a $binpeak -b $FILE > ${counts}/$CELL.txt
  done

  # make count matrices
  countsfiles=$(ls ${counts})

  for file in ${countsfiles}
  do
    cut -f 4 ${counts}/${file} > ${tmp}/${file}.count.txt
  done

  cut -f 1-3 ${binbed} > ${binfiles}/bins.txt

  paste -d '\t' ${binfiles}/bins.txt ${tmp}/*.txt > matrix.mtx

done

# now we have single cell bams and count matrices
