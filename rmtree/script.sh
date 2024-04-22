#!/bin/sh


mkdir -p test/dir1/{dir1.1,dir1.2,dir1.3}
mkdir -p test/dir1/dir1.2/{dir1.2.1,dir1.2.2,dir1.2.3}
mkdir -p test/dir2/{dir2.1,dir2.2}
mkdir -p test/dir2/dir2.2/dir2.2.1
mkdir -p test/dir2/dir2.2/{dir2.2.1,dir2.2.2}
mkdir -p test/dir3/dir3.1
mkdir -p test/dir4
mkdir -p test/dir5

touch test/dir1/dir1.1/file.scala
touch test/dir1/dir1.2/file.scala
touch test/dir2/dir2.2/{file.c,file.cpp}
touch test/dir2/dir2.2/dir2.2.2/{file.go,file.rb}
touch test/dir3/{file.js,file.java}
touch test/dir3/dir3.1/{file.c,file.cpp}
> test/dir4/file.py