TYPE=""
USAGE_MSG="Usage:\n--type [pot|mo] | -t [pot|mo] \t Generate POT file for English or compile MO files for all languages"

# Argument parsing
while [[ $# -gt 0 ]]
do
    key="$1"
    
    case $key in
        -t|--type)
            if [[ -z $TYPE && "$2" =~ (pot|mo)$ ]]; then
                TYPE="$2"
                shift # past argument
                shift # past value
            else
                echo -e $USAGE_MSG
                exit 0
            fi
        ;;
        *)    # unknown option
            echo -e $USAGE_MSG
            exit 0
        ;;
    esac
done

# No arguments
if [ -z $TYPE ]; then
    echo -e $USAGE_MSG
    exit 0
fi

# POT
if [ $TYPE = pot ]; then
    files=$(find ../src/**/*.py)
    
    if [ ! -e ./en_US/LC_MESSAGES/ape.pot ]; then
        pygettext3 -d ape -o ./en_US/LC_MESSAGES/ape.pot $files
    else
        pygettext3 $files
        
        for lang in ./*
        do
            if [ -d $lang ]; then
                msgmerge --update --no-fuzzy-matching --backup=off $lang/LC_MESSAGES/ape.pot messages.pot
            fi
        done
        rm messages.pot
    fi
    
    # MO
    elif [ $TYPE = mo ]; then
    for lang in ./*
    do
        if [ -d $lang ]; then
            msgfmt $lang/LC_MESSAGES/ape.pot --output-file $lang/LC_MESSAGES/ape.mo
        fi
    done
fi
