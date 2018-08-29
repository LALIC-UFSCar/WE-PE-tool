#!/bin/bash
USAGE_MSG="Usage:\n--srcpath path \t Path to the source file\n--srclang [pt|en] \t Source language\n--syspath path \t Path to the MT output file\n--syslang \t MT output language"

SRCPATH=""
SRCLANG=""
SYSPATH=""
SYSLANG=""

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
        --srclang)
            if [ -z $SRCLANG ]; then
                SRCLANG="$2"
                shift
                shift
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
        --syslang)
            if [ -z $SYSLANG ]; then
                SYSLANG="$2"
                shift
                shift
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
if [ -z $SRCLANG ]; then
    (>&2 echo -e $USAGE_MSG)
    exit 0
fi
if [ -z $SYSPATH ]; then
    (>&2 echo -e $USAGE_MSG)
    exit 0
fi
if [ -z $SYSLANG ]; then
    (>&2 echo -e $USAGE_MSG)
    exit 0
fi

#############
# Align words
#############
align_words() {
    SRC_FILENAME=$(basename $1)
    SYS_FILENAME=$(basename $2)

    perl Alinhador_de_Palavras/concatena_dicionario.pl $1 $2 Alinhador_de_Palavras/Dicionarios/dicionario_pt-en_v2_159814_freqmin_1.txt "/tmp/$SRC_FILENAME.concat" "/tmp/$SYS_FILENAME.concat"

    # Generate MGIZA input
    ./mgiza/mgizapp/bin/plain2snt "/tmp/$SRC_FILENAME.concat" "/tmp/$SYS_FILENAME.concat" -vcb1 "/tmp/$SRC_FILENAME.vcb" -vcb2 "/tmp/$SYS_FILENAME.vcb" -snt1 "/tmp/$SYS_FILENAME" "/tmp/$SRC_FILENAME.snt" -snt2 "/tmp/$SRC_FILENAME" "/tmp/$SYS_FILENAME.snt"

    # Generate CoocurrenceFile
    ./mgiza/mgizapp/bin/snt2cooc "/tmp/giza-cooc" "/tmp/$SRC_FILENAME.vcb" "/tmp/$SYS_FILENAME.vcb" "/tmp/$SRC_FILENAME.snt"

    # Run MGIZA
    ./mgiza/mgizapp/bin/mgiza -S "/tmp/$SRC_FILENAME.vcb" -T "/tmp/$SYS_FILENAME.vcb" -C "/tmp/$SRC_FILENAME.snt" -CoocurrenceFile "/tmp/giza-cooc"

    # perl Alinhador_de_Palavras/une_GIZA.pl "/tmp/$SRC_FILENAME.concat" "/tmp/$SYS_FILENAME.concat" r > "/tmp/giza-output"
    
    # perl Alinhador_de_Palavras/GIZA_to_PorTAl.pl "/tmp/giza-output" $1 $2 "$SRC_FILENAME.align" "$SYS_FILENAME.align" -s
}

align_words $SRCPATH $SYSPATH