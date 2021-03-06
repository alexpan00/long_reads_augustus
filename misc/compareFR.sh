#!/bin/bash
# Script para comparar los modelos con distinta longitud de la región
# flnaqueante frente a la región flanqueante más larga

# Parámetros
fr=$1       # longitud de la región flanqueantes a testear (ej: 1000,2000)
out_dir=$2  # Directorio de trabajo
out_name=$3 # Nombre para la especie y los fichero de salida
test_set=$4 # Path al fichero que contiene el set de testeo con el que se quiere comparar


# PATHS
# check if script is started via SLURM or bash
# if with SLURM: there variable '$SLURM_JOB_ID' will exist
# `if [ -n $SLURM_JOB_ID ]` checks if $SLURM_JOB_ID is not an empty string
if [ -n "$SLURM_JOB_ID" ];  then
    # check the original location through scontrol and $SLURM_JOB_ID
    SCRIPT_PATH=$(scontrol show job ${SLURM_JOB_ID} | grep Command | cut -f2 -d"=" | cut -f1 -d" ")
    echo $SCRIPT_PATH
else
    # otherwise: started with bash. Get the real location.
    SCRIPT_PATH=$(realpath -s $0)
fi

utilities=$(dirname $SCRIPT_PATH)
species_path="/home/apadepe/.conda/envs/busco/config/species/"

# Creación de un array a partir de los valores separados por comas
arrIN=(${fr//,/ })

# Creación del directorio para la comparación
mkdir $out_dir/comparison
cd $out_dir/comparison

# Comando para generar un fichero con las especies a comparar
ls -l $species_path | grep -v ${arrIN[-1]} | grep ${out_name} | grep subset | cut -f10 -d " " > $out_dir/comparison/species.txt
# Testear todos los modelos para la región flanqueante más larga
while read -r line
do
    sbatch --job-name=test$line --output $line.log \
        ${utilities}testAugustus.sbatch $line $test_set $out_dir/comparison
done < $out_dir/comparison/species.txt

# Mover los resultados y generar los plots
for i in "${arrIN[@]}"
do
    if [ i != ${arrIN[-1]} ]
    then
        mkdir fr$i
        mv *fr$i.out fr$i/
        cd fr$i
        bash ${utilities}get_stats.sh`pwd`
        Rscript ${utilities}plots.R `pwd` $out_name
        cd ..
    fi
done
        
    
