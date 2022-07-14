#!/bin/bash
SRC_NAME="abn"

# check lib exists
if [ ! -e "../src/${SRC_NAME}" ]; then
  echo "source code ../src/${SRC_NAME} not exists."
  echo "check 'SRC_NAME' in build.sh or target src directory."
  exit 0
fi


# make symbolic link
if [ ! -e ${SRC_NAME} ]; then
  ln -s ../src/${SRC_NAME} ${SRC_NAME}
  ln -s ../README.md README.md
fi


# cleanup existing htmls
make clean


# update module's *.rst
sphinx-apidoc --force -o moduledocs ${SRC_NAME}


# apply some changes on format of *.rst
# sleep 1
# for file in `ls moduledocs/${SRC_NAME}*.rst`
# do
#   echo "Reformating ${file} ..." 
#   cat ${file} \
#     | sed '/Subpackages/,/-----------/c\ ' \
#     | sed '/Submodules/,/----------/c\ ' \
#     | sed '/Module contents/,/---------------/c\ ' \
#     | sed -e "s/\(${SRC_NAME}.*\) package/\1/" \
#     | sed -e "s/\(${SRC_NAME}.*\) module/\1/" \
#     > ${file}
# done

sleep 1
for file in `ls moduledocs/${SRC_NAME}*.rst`
do
  echo "Reformating ${file} ..." 
  
  # remove section
  rst_content=`cat ${file}`
  rst_content=${rst_content//Subpackages$'\n'-----------/}
  rst_content=${rst_content//Submodules$'\n'----------/}
  rst_content=${rst_content//Module contents$'\n'---------------/}
  rst_content=${rst_content}
  echo "$rst_content" > ${file}

  # remove postfix
  cat ${file} \
    | sed -e "s/\(${SRC_NAME}.*\) package/\1/" \
    | sed -e "s/\(${SRC_NAME}.*\) module/\1/" \
    > ${file}2
  mv ${file}2 ${file} 

done


# update built html
make html


# stage html to docs
rm -rf ../docs/*
cp -rf _build/html/* ../docs
