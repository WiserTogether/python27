%define aspython2 0

%if %{aspython2}
%define python python2
%else
%define python python
%endif

%define pybasever 2.2

Summary: An interpreted, interactive, object-oriented programming language.
Name: %{python}
Version: 2.2.1
Release: 16
License: PSF - see LICENSE
Group: Development/Languages
Source: http://www.python.org/ftp/python/%{version}/Python-%{version}.tgz
Source2: idle
Source3: modulator
Source4: pynche
Source5: http://www.python.jp/pub/JapaneseCodecs/JapaneseCodecs-1.4.6.tar.gz
Patch0: python-2.2.1-config2.patch
Patch1: python-2.2b1-buildroot.patch
Patch2: python-2.2-no_ndbm.patch
Patch3: Python-2.2.1-pydocnogui.patch
Patch4: Python-2.2.1-nowhatsnew.patch
Patch5: Python-2.2.1-distutilrpm.patch
%if !%{aspython2}
Obsoletes: python2 
Provides: python2 = %{version}
BuildPrereq: db4-devel
%endif
%if !%{aspython2}
Obsoletes: Distutils
Provides: Distutils
%endif
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildPrereq: readline-devel, libtermcap-devel, openssl-devel, gmp-devel
BuildPrereq: ncurses-devel, gdbm-devel, zlib-devel, expat-devel, tetex-latex
BuildPrereq: Mesa-devel tk tix
URL: http://www.python.org/

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
%if !%{aspython2}
Obsoletes: python2-devel
Provides: python2-devel = %{version}
%endif

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
Requires: %{name} = %{version}
%if !%{aspython2}
Obsoletes: python2-tools
Provides: python2-tools = %{version}
%endif

%description tools
The Python package includes several development tools that are used
to build python programs.

%package docs
Summary: Documentation for the Python programming language.
Group: Documentation
%if !%{aspython2}
Obsoletes: python2-docs
Provides: python2-docs = %{version}
%endif

%description docs
The python-docs package contains documentation on the Python
programming language and interpreter.  The documentation is provided
in ASCII text files and in LaTeX source files.

Install the python-docs package if you'd like to use the documentation
for the Python language.

%if !%{aspython2}
%package -n tkinter
%else
%package -n tkinter2

%endif
Summary: A graphical user interface for the Python scripting language.
Group: Development/Languages
BuildPrereq:  tcl, tk
Requires: %{name} = %{version}
%if !%{aspython2}
Obsoletes: tkinter2
Provides: tkinter2 = %{version}
%endif

%if !%{aspython2}
%description -n tkinter
%else
%description -n tkinter2
%endif

The Tkinter (Tk interface) program is an graphical user interface for
the Python scripting language.

You should install the tkinter package if you'd like to use a graphical
user interface for Python programming.

%prep
%setup -q -n Python-%{version}

%patch0 -p1 -b .rhconfig
%patch1 -p1
%patch2 -p1 -b .no_ndbm
%patch3 -p1
%patch4 -p1
%patch5 -p1

# This shouldn't be necesarry, but is right now (2.2a3)
find -name "*~" |xargs rm -f

#setup -q -D -T -a 1 -n Python-%{version} -q
# This command drops the HTML files in the top-level build directory.
# That's not perfect, but it will do for now.

%build
CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC"
CXXFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC"
OPT="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC"
%configure --enable-ipv6 --enable-unicode=ucs2

make OPT="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC" %{?_smp_mflags}
Tools/scripts/pathfix.py -i "/usr/bin/env python%{pybasever}" .
make OPT="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC" %{?_smp_mflags}

%ifarch i386
pushd Doc
make
rm html/index.html.in Makefile* info/Makefile tools/sgmlconv/Makefile
popd
%endif

%install
[ -d $RPM_BUILD_ROOT ] && rm -fr $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr $RPM_BUILD_ROOT%{_mandir}

%makeinstall DESTDIR=/ MANDIR=$RPM_BUILD_ROOT/%{_mandir} INCLUDEDIR=$RPM_BUILD_ROOT/%{_includedir}
# distutils sucks.  It writes the path of the interpreter in the BUILDDIR into
# any scripts that it installs.
sed 's,#!.*/python$,#!/usr/bin/env python%{pybasever},' $RPM_BUILD_ROOT/usr/bin/pydoc > $RPM_BUILD_ROOT/usr/bin/pydoc-
mv $RPM_BUILD_ROOT/usr/bin/pydoc- $RPM_BUILD_ROOT/usr/bin/pydoc
chmod 0755 $RPM_BUILD_ROOT/usr/bin/pydoc

%if %{aspython2}
mv $RPM_BUILD_ROOT/usr/bin/python $RPM_BUILD_ROOT/usr/bin/python2
mv $RPM_BUILD_ROOT/%{_mandir}/man1/python.1 $RPM_BUILD_ROOT/%{_mandir}/man1/python%{pybasever}.1
%else
ln -s python $RPM_BUILD_ROOT/usr/bin/python2

%endif

# tools

# idle
mkdir -p ${RPM_BUILD_ROOT}/usr/lib/python%{pybasever}/site-packages
install -m 755 $RPM_SOURCE_DIR/idle ${RPM_BUILD_ROOT}/usr/bin/idle
mkdir -p $RPM_BUILD_ROOT/usr/lib/python%{pybasever}/site-packages/idle
cp -R Tools/idle/* $RPM_BUILD_ROOT/usr/lib/python%{pybasever}/site-packages/idle


#modulator
install -m 755 $RPM_SOURCE_DIR/modulator ${RPM_BUILD_ROOT}/usr/bin/modulator
cp -r Tools/modulator \
  ${RPM_BUILD_ROOT}/usr/lib/python%{pybasever}/site-packages/

#pynche
install -m 755 $RPM_SOURCE_DIR/pynche ${RPM_BUILD_ROOT}/usr/bin/pynche
rm Tools/pynche/*.pyw
cp -r Tools/pynche \
  ${RPM_BUILD_ROOT}/usr/lib/python%{pybasever}/site-packages/

mv Tools/modulator/README Tools/modulator/README.modulator
mv Tools/pynche/README Tools/pynche/README.pynche

#gettext
install -m755  Tools/i18n/pygettext.py $RPM_BUILD_ROOT/usr/bin/
install -m755  Tools/i18n/msgfmt.py $RPM_BUILD_ROOT/usr/bin/

find $RPM_BUILD_ROOT/usr/lib/python%{pybasever}/lib-dynload -type f |grep -v _tkinter.so|sed "s|$RPM_BUILD_ROOT||" > dynfiles

# Get rid of crap
find $RPM_BUILD_ROOT/ -name "*~"|xargs rm -f
find $RPM_BUILD_ROOT/ -name ".cvsignore"|xargs rm -f
find . -name "*~"|xargs rm -f
find . -name ".cvsignore"|xargs rm -f
#zero length
rm -f $RPM_BUILD_ROOT/usr/lib/python2.2/site-packages/modulator/Templates/copyright

# not distributing the testsuire
rm -fr $RPM_BUILD_ROOT/usr/lib/python2.2/test
rm -f $RPM_BUILD_ROOT/usr/lib/python2.2/LICENSE.txt


#make the binaries install side by side with python 1
%if %{aspython2}
pushd $RPM_BUILD_ROOT/usr/bin
mv idle idle2
mv modulator modulator2
mv pynche pynche2
mv pygettext.py pygettext2.py
mv msgfmt.py msgfmt2.py
mv pydoc pydoc2
popd
%endif

# Japanese codecs
tar xvzf %{SOURCE5}
pushd JapaneseCodecs-1.4.6
$RPM_BUILD_ROOT/usr/bin/python setup.py install --record=INSTALLED_FILES
popd

%clean
rm -fr $RPM_BUILD_ROOT

%files -f dynfiles
%defattr(-, root, root)
%doc LICENSE README
/usr/bin/python*
%{_mandir}/*/*

%dir /usr/lib/python%{pybasever}
%dir /usr/lib/python%{pybasever}/lib-dynload
/usr/lib/python%{pybasever}/*.py*
/usr/lib/python%{pybasever}/*.doc
/usr/lib/python%{pybasever}/curses
/usr/lib/python%{pybasever}/distutils
/usr/lib/python%{pybasever}/encodings
/usr/lib/python%{pybasever}/lib-old
/usr/lib/python%{pybasever}/plat-linux2 
/usr/lib/python%{pybasever}/site-packages
/usr/lib/python%{pybasever}/xml
/usr/lib/python%{pybasever}/email
/usr/lib/python%{pybasever}/compiler
/usr/lib/python%{pybasever}/plat-linux2
/usr/lib/python%{pybasever}/hotshot

%files devel
%defattr(-,root,root)
/usr/include/*
/usr/lib/python%{pybasever}/config

%if !%{aspython2}
%files tools
%defattr(-,root,root,755)
%doc Tools/modulator/README.modulator
%doc Tools/pynche/README.pynche
%doc Tools/idle/*.txt
%dir /usr/lib/python%{pybasever}/site-packages/idle
%dir /usr/lib/python%{pybasever}/site-packages/modulator
%dir /usr/lib/python%{pybasever}/site-packages/modulator/Templates
%dir /usr/lib/python%{pybasever}/site-packages/pynche
%dir /usr/lib/python%{pybasever}/site-packages/pynche/X
/usr/bin/idle*
/usr/bin/modulator*
/usr/bin/pynche*
/usr/bin/pygettext*.py
/usr/bin/msgfmt*.py
/usr/bin/pydoc
%endif

%files docs
%defattr(-,root,root,755)
%doc Misc/NEWS  Misc/README Misc/cheatsheet 
%doc Misc/HISTORY Doc/html

%if !%{aspython2}
%files -n tkinter
%else
%files -n tkinter2
%endif
%defattr(-,root,root,755)
/usr/lib/python%{pybasever}/lib-tk
/usr/lib/python%{pybasever}/lib-dynload/_tkinter.so

%changelog
* Tue Aug 13 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.1-16
- Fix  #71011,#71134, #58157

* Wed Aug  7 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.1-15
- Resurrect tkinter
- Fix for distutils (#67671)
- Fix #69962

* Thu Jul 25 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.1-14
- Obsolete tkinter/tkinter2 (#69838)

* Tue Jul 23 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.1-13
- Doc fixes (#53951) - not on alpha at the momemt

* Mon Jul  8 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.1-12
- fix pydoc (#68082)

* Mon Jul  8 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.1-11
- Add db4-devel as a BuildPrereq

* Fri Jun 21 2002 Tim Powers <timp@redhat.com> 2.2.1-10
- automated rebuild

* Mon Jun 17 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.1-9
- Add Japanese codecs (#66352)

* Tue Jun 11 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.1-8
- No more tkinter...

* Wed May 29 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.1-7
- Rebuild

* Tue May 21 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.1-6
- Add the email subcomponent (#65301)

* Fri May 10 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.1-5
- Rebuild

* Thu May 02 2002 Than Ngo <than@redhat.com> 2.2.1-4
- rebuild i new enviroment

* Tue Apr 23 2002 Trond Eivind Glomsrød <teg@redhat.com>
- Use ucs2, not ucs4, to avoid breaking tkinter (#63965)

* Mon Apr 22 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.1-2
- Make it use db4

* Fri Apr 12 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.1-1
- 2.2.1 - a bugfix-only release

* Fri Apr 12 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2-16
- the same, but in builddirs - this will remove them from the 
  docs package, which doesn't look in the buildroot for files.

* Fri Apr 12 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2-15
- Get rid of temporary files and .cvsignores included 
  in the tarball and make install

* Fri Apr  5 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2-14
- Don't own lib-tk in main package, only in tkinter (#62753)

* Mon Mar 25 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2-13
- rebuild

* Mon Mar 25 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2-12
- rebuild

* Fri Mar  1 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2-11
- Add a not to the Distutils obsoletes test (doh!)

* Fri Mar  1 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2-10
- Rebuild

* Mon Feb 25 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2-9
- Only obsolete Distutils when built as python

* Thu Feb 21 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2-8
- Make files in /usr/bin install side by side with python 1.5 when
- Drop explicit requirement of db4
  built as python2

* Thu Jan 31 2002 Elliot Lee <sopwith@redhat.com> 2.2-7
- Use version and pybasever macros to make updating easy
- Use _smp_mflags macro

* Tue Jan 29 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2-6
- Add db4-devel to BuildPrereq

* Fri Jan 25 2002 Nalin Dahyabhai <nalin@redhat.com> 2.2-5
- disable ndbm support, which is db2 in disguise (really interesting things
  can happen when you mix db2 and db4 in a single application)

* Thu Jan 24 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2-4
- Obsolete subpackages if necesarry 
- provide versioned python2
- build with db4

* Wed Jan 16 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2-3
- Alpha toolchain broken. Disable build on alpha.
- New openssl

* Wed Dec 26 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2-1
- 2.2 final

* Fri Dec 14 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2-0.11c1
- 2.2 RC 1
- Don't include the _tkinter module in the main package - it's 
  already in the tkiter packace
- Turn off the mpzmodule, something broke in the buildroot

* Wed Nov 28 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2-0.10b2
- Use -fPIC for OPT as well, in lack of a proper libpython.so

* Mon Nov 26 2001 Matt Wilson <msw@redhat.com> 2.2-0.9b2
- changed DESTDIR to point to / so that distutils will install dynload
  modules properly in the installroot

* Fri Nov 16 2001 Matt Wilson <msw@redhat.com> 2.2-0.8b2
- 2.2b2

* Fri Oct 26 2001 Matt Wilson <msw@redhat.com> 2.2-0.7b1
- python2ify

* Fri Oct 19 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2-0.5b1
- 2.2b1

* Sun Sep 30 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2-0.4a4
- 2.2a4
- Enable UCS4 support
- Enable IPv6
- Provide distutils
- Include msgfmt.py and pygettext.py

* Fri Sep 14 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2-0.3a3
- Obsolete Distutils, which is now part of the main package
- Obsolete python2

* Thu Sep 13 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2-0.2a3
- Add docs, tools and tkinter subpackages, to match the 1.5 layout

* Wed Sep 12 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2-0.1a3
- 2.2a3
- don't build tix and blt extensions

* Mon Aug 13 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Add tk and tix to build dependencies

* Sat Jul 21 2001 Trond Eivind Glomsrød <teg@redhat.com>
- 2.1.1 bugfix release - with a GPL compatible license

* Fri Jul 20 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Add new build dependencies (#49753)

* Tue Jun 26 2001 Nalin Dahyabhai <nalin@redhat.com>
- build with -fPIC

* Fri Jun  1 2001 Trond Eivind Glomsrød <teg@redhat.com>
- 2.1
- reorganization of file includes

* Wed Dec 20 2000 Trond Eivind Glomsrød <teg@redhat.com>
- fix the "requires" clause, it lacked a space causing problems
- use %%{_tmppath}
- don't define name, version etc
- add the available patches from the Python home page

* Fri Dec 15 2000 Matt Wilson <msw@redhat.com>
- added devel subpackage

* Fri Dec 15 2000 Matt Wilson <msw@redhat.com>
- modify all files to use "python2.0" as the intrepter
- don't build the Expat bindings
- build against db1

* Mon Oct 16 2000 Jeremy Hylton <jeremy@beopen.com>
- updated for 2.0 final

* Mon Oct  9 2000 Jeremy Hylton <jeremy@beopen.com>
- updated for 2.0c1
- build audioop, imageop, and rgbimg extension modules
- include xml.parsers subpackage
- add test.xml.out to files list

* Thu Oct  5 2000 Jeremy Hylton <jeremy@beopen.com>
- added bin/python2.0 to files list (suggested by Martin v. Löwis)

* Tue Sep 26 2000 Jeremy Hylton <jeremy@beopen.com>
- updated for release 1 of 2.0b2
- use .bz2 version of Python source

* Tue Sep 12 2000 Jeremy Hylton <jeremy@beopen.com>
- Version 2 of 2.0b1
- Make the package relocatable.  Thanks to Suchandra Thapa.
- Exclude Tkinter from main RPM.  If it is in a separate RPM, it is
  easier to track Tk releases.
