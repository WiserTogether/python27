# Makefile for source rpm: python
# $Id$
NAME := python
SPECFILE = $(firstword $(wildcard *.spec))

include ../common/Makefile.common
