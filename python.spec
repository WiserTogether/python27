%define	tcltk_major	8.3
%define	tkinter_tcldeps	libtcl%{tcltk_major}.so libtk%{tcltk_major}.so libtix4.1.%{tcltk_major}.so

Summary: An interpreted, interactive object-oriented programming language.
Name: python
Version: 1.5.2
Release: 25
Copyright: distributable
Group: Development/Languages
Source0: ftp://ftp.python.org/pub/python/src/py152.tgz
Source1: Python-Doc.tar.gz
Source2: idle
Source3: modulator
Source4: pynche
Patch0: python-1.5.2-config.patch
Patch1: python-1.4-gccbug.patch
Patch2: Python-1.5.1-nosed.patch
Patch3: python-1.5.2-dl-global.patch
Patch4: python-1.5.2-pythonpath.patch
Patch5: python-1.5.2-wdb.patch
Patch6: python-1.5.2-wuftpd.patch
Patch7: python-1.5.2-_locale.patch
Patch8: python-1.5.2-tcl831.patch
BuildRequires: readline readline-devel zlib zlib-devel gmp gmp-devel gdbm gdbm-devel
Conflicts: tkinter < %{PACKAGE_VERSION}
BuildRoot: %{_tmppath}/%{name}/python-root

%description
Python is an interpreted, interactive, object-oriented programming
language often compared to Tcl, Perl, Scheme or Java. Python includes
modules, classes, exceptions, very high level dynamic data types and
dynamic typing. Python supports interfaces to many system calls and
libraries, as well as to various windowing systems (X11, Motif, Tk,
Mac and MFC).

Programmers can write new built-in modules for Python in C or C++.
Python can be used as an extension language for applications that need
a programmable interface. This package contains most of the standard
Python modules, as well as modules for interfacing to the Tix widget
set for Tk and RPM.

Note that documentation for Python is provided in the python-docs
package.

%package devel
Summary: The libraries and header files needed for Python development.
Group: Development/Libraries
Requires: python = %{PACKAGE_VERSION}

%description devel
The Python programming language's interpreter can be extended with
dynamically loaded extensions and can be embedded in other programs.
This package contains the header files and libraries needed to do
these types of tasks.

Install python-devel if you want to develop Python extensions.  The
python package will also need to be installed.  You'll probably also
want to install the python-docs package, which contains Python
documentation.

%package tools
Summary: A collection of development tools included with Python.
Group: Development/Tools
Requires: python = %{PACKAGE_VERSION}

%description tools
The Python package includes several development tools that are used
to build python programs.  This package contains a selection of those
tools, including the IDLE Python IDE.

Install python-tools if you want to use these tools to develop
Python programs.  You will also need to install the python and
tkinter packages.

%package docs
Summary: Documentation for the Python programming language.
Group: Documentation
Conflicts: python < %{PACKAGE_VERSION}

%description docs
The python-docs package contains documentation on the Python
programming language and interpreter.  The documentation is provided
in ASCII text files and in LaTeX source files.

Install the python-docs package if you'd like to use the documentation
for the Python language.

%package -n tkinter
Summary: A graphical user interface for the Python scripting language.
Group: Development/Languages
BuildPrereq: %{tkinter_tcldeps}
Requires: python = %{PACKAGE_VERSION}

%description -n tkinter
The Tkinter (Tk interface) program is an graphical user interface for
the Python scripting language.

You should install the tkinter package if you'd like to use a graphical
user interface for Python programming.

%prep
%setup -q -n Python-1.5.2 -a 1
%patch0 -p1 -b .config

#%ifarch alpha
#%patch1 -p1
#%endif
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1 -b ._locale
%patch8 -p1 -b .tcl823

find . -name "*.nosed" -exec rm -f {} \;

echo ': ${LDSHARED='gcc -shared'}' > config.cache
echo ': ${LINKFORSHARED='-rdynamic'}' >> config.cache
echo ': ${CCSHARED='-fPIC'}' >> config.cache

cp Lib/lib-old/rand.py Lib

%build
export MACHDEP=linux-$RPM_ARCH
%configure --with-threads

LDFLAGS=-s make 

%install
rm -rf ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}%{_prefix}/{bin,lib}

#make install prefix=${RPM_BUILD_ROOT}%{_prefix}
%makeinstall
strip ${RPM_BUILD_ROOT}%{_bindir}/python

# tools
# idle
mkdir -p ${RPM_BUILD_ROOT}%{_prefix}/lib/python1.5/site-packages
install -m 755 $RPM_SOURCE_DIR/idle ${RPM_BUILD_ROOT}%{_bindir}/idle
mkdir -p ${RPM_BUILD_ROOT}%{_prefix}/lib/python1.5/site-packages/idle
cp Tools/idle/*.py \
  ${RPM_BUILD_ROOT}%{_prefix}/lib/python1.5/site-packages/idle/
mv Tools/idle/help.txt \
  ${RPM_BUILD_ROOT}%{_prefix}/lib/python1.5/site-packages/idle/
mv Tools/idle/extend.txt \
  ${RPM_BUILD_ROOT}%{_prefix}/lib/python1.5/site-packages/idle/

#modulator
install -m 755 $RPM_SOURCE_DIR/modulator ${RPM_BUILD_ROOT}%{_bindir}/modulator
cp -r Tools/modulator \
  ${RPM_BUILD_ROOT}%{_prefix}/lib/python1.5/site-packages/

#pynche
install -m 755 $RPM_SOURCE_DIR/pynche ${RPM_BUILD_ROOT}%{_bindir}/pynche
rm Tools/pynche/*.pyw
cp -r Tools/pynche \
  ${RPM_BUILD_ROOT}%{_prefix}/lib/python1.5/site-packages/

mv Tools/modulator/README Tools/modulator/README.modulator
mv Tools/pynche/README Tools/pynche/README.pynche

rm -f modules-list.full
for n in ${RPM_BUILD_ROOT}%{_prefix}/lib/python1.5/*; do
  [ -d $n ] || echo $n
done >> modules-list.full

for mod in ${RPM_BUILD_ROOT}%{_prefix}/lib/python1.5/lib-dynload/* ; do
  [ `basename $mod` = _tkinter.so ] || echo $mod
done >> modules-list.full
sed -e "s|${RPM_BUILD_ROOT}||g" < modules-list.full > modules-list

#get files list for python-tools
DIR1=${RPM_BUILD_ROOT}%{_prefix}/lib/python1.5/site-packages/pynche
DIR2=${RPM_BUILD_ROOT}%{_prefix}/lib/python1.5/site-packages/idle
DIR3=${RPM_BUILD_ROOT}%{_prefix}/lib/python1.5/site-packages/modulator

find $DIR1 -type f | sed -e "s#^${RPM_BUILD_ROOT}##g" > python-tools.files
find $DIR2 -type f | sed -e "s#^${RPM_BUILD_ROOT}##g" >> python-tools.files
find $DIR3 -type f | sed -e "s#^${RPM_BUILD_ROOT}##g" >> python-tools.files

#rebytecompile modules with the right directory names
find $RPM_BUILD_ROOT%{_prefix}/lib/python1.5 -type f -name "*.pyc" | xargs rm -v
PYTHONPATH=$RPM_BUILD_ROOT%{_prefix}/lib/python1.5 $RPM_BUILD_ROOT%{_bindir}/python -c "import compileall; compileall.compile_dir('"$RPM_BUILD_ROOT"/usr/lib/python1.5', 4, '/usr/lib/python1.5/site-packages')"

%clean
rm -rf ${RPM_BUILD_ROOT}
rm -f modules-list modules-list.full

%files -f modules-list
%defattr(-,root,root,755)
%{_bindir}/python*
%dir %{_prefix}/lib/python1.5
%{_prefix}/lib/python1.5/plat-linux-%{_target_cpu}
%{_prefix}/lib/python1.5/lib-stdwin
%dir %{_prefix}/lib/python1.5/lib-dynload

%files devel
%defattr(-,root,root,755)
%{_prefix}/lib/python*/test
%{_prefix}/lib/python*/config
%{_prefix}/include/python1.5

%files -f python-tools.files tools
%defattr(-,root,root,755)
%doc Tools/idle/*.txt
%doc Tools/modulator/README.modulator
%doc Tools/pynche/README.pynche
%dir %{_prefix}/lib/python1.5/site-packages/idle
%dir %{_prefix}/lib/python1.5/site-packages/modulator
%dir %{_prefix}/lib/python1.5/site-packages/modulator/Templates
%dir %{_prefix}/lib/python1.5/site-packages/pynche
%dir %{_prefix}/lib/python1.5/site-packages/pynche/X
%{_bindir}/idle
%{_bindir}/modulator
%{_bindir}/pynche

%files docs
%defattr(-,root,root,755)
%doc Misc/COPYRIGHT Misc/NEWS Misc/HYPE Misc/README Misc/cheatsheet Misc/BLURB* 
%doc Misc/HISTORY Doc

%files -n tkinter
%defattr(-,root,root,755)
%{_prefix}/lib/python1.5/lib-tk
%{_prefix}/lib/python1.5/lib-dynload/_tkinter.so

%changelog
* Wed Aug 23 2000 Nalin Dahyabhai <nalin@redhat.com>
- byte-compile modules with the correct directory paths

* Mon Jul 31 2000 Matt Wilson <msw@redhat.com>
- fixed directory perms from 775 to 755 to make rpmlint shut up

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Mon Jun 18 2000 Bill Nottingham <notting@redhat.com>
- rebuild, fix dependencies

* Thu Jun 15 2000 Matt Wilson <msw@redhat.com>
- rebuilt against new tcltk

* Sat Jun  3 2000 Jeff Johnson <jbj@redhat.com>
- rebuild against tcltk 8.3.1.

* Fri Apr 28 2000 Matt Wilson <msw@redhat.com>
- rebuild against gmp 3.0.1

* Wed Apr  5 2000 Bill Nottingham <notting@redhat.com>
- what he said

* Tue Mar 21 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- rebuild with readline 4.1

* Sat Mar 18 2000 Jeff Johnson <jbj@redhat.com>
- rebuild tkinter against tcl-8.2.3.

* Thu Mar 09 2000 Nalin Dahyabhai <nalin@redhat.com>
- build _localemodule.so to fix bug #9385 (release 14)

* Tue Feb 01 2000 Cristian Gafton <gafton@redhat.com>
- add patch tp fix problems talioking to wuftpd from hjl
- rebuild to fix dependencies

* Mon Jan 31 2000 Nalin Dahyabhai <nalin@redhat.com>
- add buildrequires lines (#8925)

* Mon Jan 17 2000 Nalin Dahyabhai <nalin@redhat.com>
- put idle, modulator, and pynche only in python-tools

* Thu Dec 02 1999 Michael K. Johnson <johnsonm@redhat.com>
- fixed whichdb patch to actually do something (#7458)

* Mon Nov 22 1999 Michael K. Johnson <johnsonm@redhat.com>
- link nismodule against -lnss
- whichdb patch by Guido (Python.org bug 97)

* Fri Sep 17 1999 Tim Powers <timp@redhat.com>
- added modulator and pynche to the python-tools package
- using a files list in the %files section for python-tools

* Fri Sep 17 1999 Michael K. Johnson <johnsonm@redhat.com>
- added conflicts/requires between subpackages so that you cannot
  have an older tkinter installed with a new python.
- added more tools

* Wed Sep 15 1999 Michael K. Johnson <johnsonm@redhat.com>
- changed defattr so that executable scripts in docs stay executable

* Tue Aug 24 1999 Bill Nottingham <notting@redhat.com>
- rebuild to fix broken tkinter.

* Mon Aug  9 1999 Matt Wilson <msw@redhat.com>
- fixed bogus /usr/local/bin/python requirements

* Sat Jul 17 1999 Matt Wilson <msw@redhat.com>
- added patch to import global symbols until we get libtool patched

* Sun Jul 11 1999 Matt Wilson <msw@redhat.com>
- updated to 1.5.2

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 10)

* Thu Mar 18 1999 Bill Nottingham <notting@redhat.com>
- fix permissions in python-docs

* Thu Feb 11 1999 Michael Johnson <johnsonm@redhat.com>
- added mpzmodule at user request (uses gmp)
- added bsddbmodule at user request (uses db 1.85 interface)

* Mon Feb 08 1999 Michael Johnson <johnsonm@redhat.com>
- add --with-threads at user request
- clean up spec file

* Fri Jan 08 1999 Michael K. Johnson <johnsonm@redhat.com>
- New libc changes ndbm.h to db1/ndbm.h and -ldb to -ldb1

* Thu Sep  3 1998 Jeff Johnson <jbj@redhat.com>
- recompile for RH 5.2.

* Wed May 06 1998 Cristian Gafton <gafton@redhat.com>
- python-docs used to require /usr/bin/sed. Changed to /bin/sed instead

* Wed Apr 29 1998 Cristian Gafton <gafton@redhat.com>
- fixed the spec file for version 1.5.1
- buildroot (!)

* Mon Apr 20 1998 Michael K. Johnson <johnsonm@redhat.com>
- updated to python 1.5.1
- created our own Python-Doc tar file from 1.5 to substitute for the
  not-yet-released Doc package.
- build _tkinter properly
- use readline again
- build crypt module again
- install rand replacement module
- added a few modules

* Thu Apr 09 1998 Erik Troan <ewt@redhat.com>
- updated to python 1.5
- made /usr/lib/python1.5 file list automatically generated

* Tue Nov 04 1997 Michael K. Johnson <johnsonm@redhat.com>
- Fixed dependencies for python and tkinter

* Mon Nov 03 1997 Michael K. Johnson <johnsonm@redhat.com>
- pulled out tk-related stuff into tkinter package

* Fri Oct 10 1997 Erik Troan <ewt@redhat.com>
- bunches of scripts used /usr/local/bin/python instead of /usr/bin/python

* Tue Sep 30 1997 Erik Troan <ewt@redhat.com>
- updated for tcl/tk 8.0

* Thu Jul 10 1997 Erik Troan <ewt@redhat.com>
- built against glibc
