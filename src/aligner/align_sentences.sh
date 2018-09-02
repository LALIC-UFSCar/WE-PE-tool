#!/bin/bash
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
USAGE_MSG="Usage:\n--srcpath path \t Path to the source file\n--srclang [pt|en] \t --syspath path \t Path to the MT output file"

SRCPATH=""
SYSPATH=""

##################
# Argument parsing
##################
while [[ $# -gt 0 ]]
do
    key="$1"
    
    case $key in
        --srcpath)
            if [ -z $SRCPATH ]; then
                SRCPATH="$2"
                shift # past argument
                shift # past value
            else
                (>&2 echo -e $USAGE_MSG)
                exit 0
            fi
        ;;
        --syspath)
            if [ -z $SYSPATH ]; then
                SYSPATH="$2"
                shift # past argument
                shift # past value
            else
                (>&2 echo -e $USAGE_MSG)
                exit 0
            fi
        ;;
            *)    # unknown option
            (>&2 echo -e $USAGE_MSG)
            exit 0
        ;;
    esac
done

# No arguments
if [ -z $SRCPATH ]; then
    (>&2 echo -e $USAGE_MSG)
    exit 0
fi
if [ -z $SYSPATH ]; then
    (>&2 echo -e $USAGE_MSG)
    exit 0
fi

#############
# Align words
#############
align_words() {
    SRC_FILENAME=$(basename $1)
    SYS_FILENAME=$(basename $2)

    perl Alinhador_de_Palavras/concatena_dicionario.pl $1 $2 Alinhador_de_Palavras/Dicionarios/dicionario_en-pt_v2_158037_freqmin_1.txt "/tmp/$SRC_FILENAME.concat" "/tmp/$SYS_FILENAME.concat"

    # Generate MGIZA input
    $SCRIPTPATH/mgiza/mgizapp/bin/plain2snt "/tmp/$SRC_FILENAME.concat" "/tmp/$SYS_FILENAME.concat" -vcb1 "/tmp/$SRC_FILENAME.vcb" -vcb2 "/tmp/$SYS_FILENAME.vcb" -snt1 "/tmp/$SRC_FILENAME-$SYS_FILENAME.snt" -snt2 "/tmp/$SYS_FILENAME-$SRC_FILENAME.snt"

    # Generate CoocurrenceFile
    $SCRIPTPATH/mgiza/mgizapp/bin/snt2cooc "/tmp/giza-cooc" "/tmp/$SRC_FILENAME.vcb" "/tmp/$SYS_FILENAME.vcb" "/tmp/$SYS_FILENAME-$SRC_FILENAME.snt"

    cd /tmp/
    # Run MGIZA
    $SCRIPTPATH/mgiza/mgizapp/bin/mgiza -S "/tmp/$SRC_FILENAME.vcb" -T "/tmp/$SYS_FILENAME.vcb" -C "/tmp/$SRC_FILENAME-$SYS_FILENAME.snt" -CoocurrenceFile "/tmp/giza-cooc"
    cat *.final.part* > giza.output
    rm *.final.*
    cd $SCRIPTPATH
    head -n$(wc -l < $1) /tmp/giza.output > aligned_sentences.output
}

align_words $SRCPATH $SYSPATH
