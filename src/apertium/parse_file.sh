#!/bin/bash
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
LANG=""
USAGE_MSG="Usage:\n--lang [pt|en] | -l [pt|en] \t Language to parse using the Apertium parser"

# Argument parsing
while [[ $# -gt 0 ]]
do
    key="$1"
    
    case $key in
        -l|--lang)
            if [[ -z $LANG && "$2" =~ (pt|en)$ ]]; then
                LANG="$2"
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
if [ -z $LANG ]; then
    (>&2 echo -e $USAGE_MSG)
    exit 0
fi

# Check if tools are installed
if ! [ -x "$(command -v lt-proc)" ]; then
    (>&2 echo "Please install lt-proc by running \"sudo apt install lttoolbox-dev\"")
    exit 0
fi
if ! [ -x "$(command -v apertium-tagger)" ]; then
    (>&2 echo "Please install apertium-tagger by running \"sudo apt install apertium\"")
    exit 0
fi

# Use supported locale
export LC_ALL="en_US.UTF-8"

# Tag input
read data
data=$(echo $data | sed 's/@-@/-/g') # Replace Moses format @-@ to -
data=$(echo $data | sed 's/\(\w\)\s\$\s\([[:digit:]]\)/\1\2/g') # Change currency from format US $ 1 to US$1
data=$(echo $data | sed 's/>/~/g') # Replace > to ~
analysis_output=$(echo $data | lt-proc -a $SCRIPTPATH/apertium-$LANG/$LANG.automorf_retratos.bin)
tagger_output=$(echo $analysis_output | apertium-tagger -g $SCRIPTPATH/apertium-$LANG/$LANG.prob)
tagger_output=$(echo $tagger_output | sed 's/~/^>$/g') # Replace ~ back to > and add token delimiters
tagger_output=$(echo $tagger_output | sed 's/\"/\^\"\$/g') # Add start and end of token to upper commas
tagger_output=$(echo $tagger_output | sed 's/#\s/$ ^ /g') # Add start and end of token to # tokens
tagger_output=$(echo $tagger_output | sed 's/\s-\s/ ^-$ /g') # Add start and end of token to - tokens
echo $tagger_output
