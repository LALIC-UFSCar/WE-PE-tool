for file in ../src/**/*
do
    if [ ${file: -3} == ".py" ]
    then
        filename=$(basename -- "$file")
        filename="${filename%.*}"

        pygettext3 -d $filename -o ./$filename.pot $file
    fi
done
