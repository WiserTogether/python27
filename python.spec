%define aspython2 0
%define unicode ucs4

%if %{aspython2}
%define python python2
%else
%define python python
%endif

%define pybasever 2.3
%define jp_codecs 1.4.9

Summary: An interpreted, interactive, object-oriented programming language.
Name: %{python}
Version: %{pybasever}.4
Release: 2
License: PSF - see LICENSE
Group: Development/Languages
Provides: python-abi = %{pybasever}
Source: http://www.python.org/ftp/python/%{version}/Python-%{version}.tar.bz2
Source3: modulator
Source4: pynche
Source5: http://www.python.jp/pub/JapaneseCodecs/JapaneseCodecs-%{jp_codecs}.tar.gz
Source6: http://gigue.peabody.jhu.edu/~mdboom/omi/source/shm_source/shmmodule.c

Patch0: python-2.3-config.patch
Patch3: Python-2.2.1-pydocnogui.patch
Patch4: python-2.3-nowhatsnew.patch
Patch7: python-2.3.4-lib64-regex.patch
Patch8: python-2.3.2-lib64.patch
Patch9: japanese-codecs-lib64.patch
Patch12: python-2.3.2-nomkhowto.patch
Patch13: python-2.3.4-distutils-bdist-rpm.patch

%if !%{aspython2}
Obsoletes: python2 
Provides: python2 = %{version}
BuildPrereq: db4-devel
%else
BuildPrereq: db3-devel
%endif
%if !%{aspython2}
Obsoletes: Distutils
Provides: Distutils
%endif

BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildPrereq: readline-devel, libtermcap-devel, openssl-devel, gmp-devel
BuildPrereq: ncurses-devel, gdbm-devel, zlib-devel, expat-devel, tetex-latex
BuildPrereq: Mesa-devel tk tix gcc-c++ XFree86-devel glibc-devel
BuildPrereq: gzip tar /usr/bin/find pkgconfig tcl-devel tk-devel
BuildPrereq: tix-devel
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
Requires: tkinter = %{version}
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
%setup -q -n Python-%{version} -a 5

%patch0 -p1 -b .rhconfig
%patch3 -p1 -b .no_gui
%patch4 -p1
%if %{_lib} == lib64
%patch7 -p1 -b .lib64-regex
%patch8 -p1 -b .lib64
%patch9 -p0 -b .lib64-j
%endif
%patch12 -p1 -b .nomkhowto
%patch13 -p1 -b .bdist-rpm

# This shouldn't be necesarry, but is right now (2.2a3)
find -name "*~" |xargs rm -f

# Temporary workaround to avoid confusing find-requires: don't ship the tests
# as executable files
chmod 0644 Lib/test/test_*.py

# shm module
cp %{SOURCE6} Modules
cat >> Modules/Setup.dist << EOF

# Shared memory module
shm shmmodule.c
EOF

%build
topdir=`pwd`
export CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC"
export CXXFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC"
export OPT="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC"
export LINKCC="gcc"
if pkg-config openssl ; then
	export CFLAGS="$CFLAGS `pkg-config --cflags openssl`"
	export LDFLAGS="$LDFLAGS `pkg-config --libs-only-L openssl`"
fi
# Force CC
export CC=gcc
%configure --enable-ipv6 --enable-unicode=%{unicode}

make OPT="$CFLAGS" %{?_smp_mflags}
$topdir/python Tools/scripts/pathfix.py -i "/usr/bin/env python%{pybasever}" .
make OPT="$CFLAGS" %{?_smp_mflags}

%ifarch i386
pushd Doc
make PYTHON=$topdir/python
rm html/index.html.in Makefile* info/Makefile tools/sgmlconv/Makefile
popd
%endif

%install
[ -d $RPM_BUILD_ROOT ] && rm -fr $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr $RPM_BUILD_ROOT%{_mandir}

# Clean up patched .py files that are saved as .lib64
for f in distutils/command/install distutils/sysconfig; do
    rm -f Lib/$f.py.lib64
done

%makeinstall DESTDIR=/ MANDIR=$RPM_BUILD_ROOT%{_mandir} INCLUDEDIR=$RPM_BUILD_ROOT%{_includedir} LIBDIR=$RPM_BUILD_ROOT%{_libdir} SCRIPTDIR=$RPM_BUILD_ROOT%{_libdir} build_root=$RPM_BUILD_ROOT
# Fix the interpreter path in binaries installed by distutils 
# (which changes them by itself)
# Make sure we preserve the file permissions
for fixed in $RPM_BUILD_ROOT/usr/bin/pydoc; do
    sed 's,#!.*/python$,#!/usr/bin/env python%{pybasever},' $fixed > $fixed- \
        && cat $fixed- > $fixed && rm -f $fixed-
done

%if %{aspython2}
mv $RPM_BUILD_ROOT/usr/bin/python $RPM_BUILD_ROOT/usr/bin/python2
mv $RPM_BUILD_ROOT/%{_mandir}/man1/python.1 $RPM_BUILD_ROOT/%{_mandir}/man1/python%{pybasever}.1
%else
ln -s python $RPM_BUILD_ROOT/usr/bin/python2
%endif

# tools

mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/python%{pybasever}/site-packages

#modulator
install -m 755 $RPM_SOURCE_DIR/modulator ${RPM_BUILD_ROOT}/usr/bin/modulator
cp -r Tools/modulator \
  ${RPM_BUILD_ROOT}%{_libdir}/python%{pybasever}/site-packages/

#pynche
install -m 755 $RPM_SOURCE_DIR/pynche ${RPM_BUILD_ROOT}/usr/bin/pynche
rm -f Tools/pynche/*.pyw
cp -r Tools/pynche \
  ${RPM_BUILD_ROOT}%{_libdir}/python%{pybasever}/site-packages/

mv Tools/modulator/README Tools/modulator/README.modulator
mv Tools/pynche/README Tools/pynche/README.pynche

#gettext
install -m755  Tools/i18n/pygettext.py $RPM_BUILD_ROOT/usr/bin/
install -m755  Tools/i18n/msgfmt.py $RPM_BUILD_ROOT/usr/bin/

# Get rid of crap
find $RPM_BUILD_ROOT/ -name "*~"|xargs rm -f
find $RPM_BUILD_ROOT/ -name ".cvsignore"|xargs rm -f
find . -name "*~"|xargs rm -f
find . -name ".cvsignore"|xargs rm -f
#zero length
rm -f $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/site-packages/modulator/Templates/copyright

# Clean up the testsuite - we don't need compiled files for it
find $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/test \
    -name "*.pyc" -o -name "*.pyo" | xargs rm -f
rm -f $RPM_BUILD_ROOT%{_libdir}/python2.2/LICENSE.txt


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
pushd JapaneseCodecs-%{jp_codecs}
PYTHONHOME=$RPM_BUILD_ROOT/usr $RPM_BUILD_ROOT/usr/bin/%{python} setup.py \
install \
--install-scripts=$RPM_BUILD_ROOT/%{_prefix}/bin \
--install-purelib=$RPM_BUILD_ROOT/%{_libdir}/python%{pybasever}/site-packages \
--install-platlib=$RPM_BUILD_ROOT/%{_libdir}/python%{pybasever}/lib-dynload \
--install-data=$RPM_BUILD_ROOT/%{_exec_prefix} \
--root=/
popd

find $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/lib-dynload -type f | grep -v _tkinter.so | sed "s|$RPM_BUILD_ROOT||" > dynfiles

%clean
rm -fr $RPM_BUILD_ROOT

%files -f dynfiles
%defattr(-, root, root)
%doc LICENSE README
/usr/bin/python*
%if %{aspython2}
/usr/bin/idle2
/usr/bin/modulator2
/usr/bin/msgfmt2.py
/usr/bin/pydoc2
/usr/bin/pygettext2.py
/usr/bin/pynche2
%endif
%{_mandir}/*/*

%dir %{_libdir}/python%{pybasever}
%dir %{_libdir}/python%{pybasever}/lib-dynload
%dir %{_libdir}/python%{pybasever}/lib-dynload/japanese
%{_libdir}/python%{pybasever}/site-packages/japanese.pth
%dir %{_libdir}/python%{pybasever}/site-packages
%{_libdir}/python%{pybasever}/site-packages/README
%{_libdir}/python%{pybasever}/LICENSE.txt
%{_libdir}/python%{pybasever}/*.py*
%{_libdir}/python%{pybasever}/*.doc
%{_libdir}/python%{pybasever}/bsddb
%dir %{_libdir}/python%{pybasever}/config
%{_libdir}/python%{pybasever}/config/Makefile
%{_libdir}/python%{pybasever}/curses
%{_libdir}/python%{pybasever}/distutils
%{_libdir}/python%{pybasever}/encodings
%{_libdir}/python%{pybasever}/idlelib
%{_libdir}/python%{pybasever}/lib-old
%{_libdir}/python%{pybasever}/logging
%{_libdir}/python%{pybasever}/xml
%{_libdir}/python%{pybasever}/email
%{_libdir}/python%{pybasever}/compiler
%{_libdir}/python%{pybasever}/plat-linux2
%{_libdir}/python%{pybasever}/hotshot

%files devel
%defattr(-,root,root)
/usr/include/*
%{_libdir}/python%{pybasever}/config
%{_libdir}/python%{pybasever}/test

%if !%{aspython2}
%files tools
%defattr(-,root,root,755)
%doc Tools/modulator/README.modulator
%doc Tools/pynche/README.pynche
%{_libdir}/python%{pybasever}/site-packages/modulator
%{_libdir}/python%{pybasever}/site-packages/pynche
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
%{_libdir}/python%{pybasever}/lib-tk
%{_libdir}/python%{pybasever}/lib-dynload/_tkinter.so

%changelog
* Mon Jun  7 2004 Mihai Ibanescu <misa@redhat.com> 2.3.4-2
- Patched bdist_rpm to allow for builds of multiple binary rpms (bug #123598)

* Fri Jun  4 2004 Mihai Ibanescu <misa@redhat.com> 2.3.4-1
- Updated to 2.3.4-1 with Robert Scheck's help (bug #124764)
- Added BuildRequires: tix-devel (bug #124918)

* Fri May  7 2004 Mihai Ibanescu <misa@redhat.com> 2.3.3-6
- Correct fix for #122304 from upstream:
  http://sourceforge.net/tracker/?func=detail&atid=105470&aid=931848&group_id=5470

* Thu May  6 2004 Mihai Ibanescu <misa@redhat.com> 2.3.3-4
- Fix for bug #122304 : splitting the domain name fails on 64-bit arches
- Fix for bug #120879 : including Makefile into the main package

- Requires XFree86-devel instead of -libs (see bug #118442)

* Tue Mar 16 2004 Mihai Ibanescu <misa@redhat.com> 2.3.3-3
- Requires XFree86-devel instead of -libs (see bug #118442)

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Dec 19 2003 Jeff Johnson <jbj@jbj.org> 2.3.3-1
- upgrade to 2.3.3.

* Sat Dec 13 2003 Jeff Johnson <jbj@jbj.org> 2.3.2-9
- rebuild against db-4.2.52.

* Fri Dec 12 2003 Jeremy Katz <katzj@redhat.com> 2.3.2-8
- more rebuilding for new tcl/tk

* Wed Dec  3 2003 Jeff Johnson <jbj@jbj.org> 2.3.2-7.1
- rebuild against db-4.2.42.

* Fri Nov 28 2003 Mihai Ibanescu <misa@redhat.com> 2.3.2-7
- rebuilt against newer tcl/tk

* Mon Nov 24 2003 Mihai Ibanescu <misa@redhat.com> 2.3.2-6
- added a Provides: python-abi

* Wed Nov 12 2003 Mihai Ibanescu <misa@redhat.com> 2.3.2-5
- force CC (#109268)

* Sun Nov  9 2003 Jeremy Katz <katzj@redhat.com> 2.3.2-4
- cryptmodule still needs -lcrypt

* Wed Nov  5 2003 Mihai Ibanescu <misa@redhat.com> 2.3.2-2
- Added patch for missing mkhowto

* Thu Oct 16 2003 Mihai Ibanescu <misa@redhat.com> 2.3.2-1
- Updated to 2.3.2

* Thu Sep 25 2003 Mihai Ibanescu <misa@redhat.com> 2.3.1-1
- 2.3.1 final

* Tue Sep 23 2003 Mihai Ibanescu <misa@redhat.com> 2.3.1-0.8.RC1
- Building the python 2.3.1 release candidate
- Updated the lib64 patch

* Wed Jul 30 2003 Mihai Ibanescu <misa@redhat.com> 2.3-0.2
- Building python 2.3
- Added more BuildRequires
- Updated the startup files for modulator and pynche; idle installs its own
  now.

* Thu Jul  3 2003 Mihai Ibanescu <misa@redhat.com> 2.2.3-4
- Rebuilt against newer db4 packages (bug #98539)

* Mon Jun 9 2003 Elliot Lee <sopwith@redhat.com> 2.2.3-3
- rebuilt

* Wed Jun  7 2003 Mihai Ibanescu <misa@redhat.com> 2.2.3-2
- Rebuilt

* Tue Jun  6 2003 Mihai Ibanescu <misa@redhat.com> 2.2.3-1
- Upgraded to 2.2.3

* Wed Apr  2 2003 Mihai Ibanescu <misa@redhat.com> 2.2.2-28
- Rebuilt

* Wed Apr  2 2003 Mihai Ibanescu <misa@redhat.com> 2.2.2-27
- Modified the ftpuri patch conforming to http://ietf.org/rfc/rfc1738.txt

* Mon Feb 24 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Feb 24 2003 Mihai Ibanescu <misa@redhat.com> 2.2.2-25
- Fixed bug #84886: pydoc dies when run w/o arguments
- Fixed bug #84205: add python shm module back (used to be shipped with 1.5.2)
- Fixed bug #84966: path in byte-compiled code still wrong

* Thu Feb 20 2003 Jeremy Katz <katzj@redhat.com> 2.2.2-23
- ftp uri's should be able to specify being rooted at the root instead of 
  where you login via ftp (#84692)

* Mon Feb 10 2003 Mihai Ibanescu <misa@redhat.com> 2.2.2-22
- Using newer Japanese codecs (1.4.9). Thanks to 
  Peter Bowen <pzb@datastacks.com> for pointing this out.

* Thu Feb  6 2003 Mihai Ibanescu <misa@redhat.com> 2.2.2-21
- Rebuild

* Wed Feb  5 2003 Mihai Ibanescu <misa@redhat.com> 2.2.2-20
- Release number bumped really high: turning on UCS4 (ABI compatibility
  breakage)

* Fri Jan 31 2003 Mihai Ibanescu <misa@redhat.com> 2.2.2-13
- Attempt to look both in /usr/lib64 and /usr/lib/python2.2/site-packages/:
  some work on python-2.2.2-lib64.patch

* Thu Jan 30 2003 Mihai Ibanescu <misa@redhat.com> 2.2.2-12
- Rebuild to incorporate the removal of .lib64 and - files.

* Thu Jan 30 2003 Mihai Ibanescu <misa@redhat.com> 2.2.2-11.7.3
- Fixed bug #82544: Errata removes most tools
- Fixed bug #82435: Python 2.2.2 errata breaks redhat-config-users
- Removed .lib64 and - files that get installed after we fix the multilib
  .py files.

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Wed Jan 15 2003 Jens Petersen <petersen@redhat.com> 2.2.2-10
- rebuild to update tkinter's tcltk deps
- convert changelog to utf-8

* Tue Jan  7 2003 Nalin Dahyabhai <nalin@redhat.com> 2.2.2-9
- rebuild

* Fri Jan  3 2003 Nalin Dahyabhai <nalin@redhat.com>
- pick up OpenSSL cflags and ldflags from pkgconfig if available

* Thu Jan  2 2003 Jeremy Katz <katzj@redhat.com> 2.2.2-8
- urllib2 didn't support non-anonymous ftp.  add support based on how 
  urllib did it (#80676, #78168)

* Mon Dec 16 2002 Mihai Ibanescu <misa@redhat.com> 2.2.2-7
- Fix bug #79647 (Rebuild of SRPM fails if python isn't installed)
- Added a bunch of missing BuildRequires found while fixing the
  above-mentioned bug

* Tue Dec 10 2002 Tim Powers <timp@redhat.com> 2.2.2-6
- rebuild to fix broken tcltk deps for tkinter

* Fri Nov 22 2002 Mihai Ibanescu <misa@redhat.com>
2.2.2-3.7.3
- Recompiled for 7.3 (to fix the -lcrypt bug)
- Fix for the spurious error message at the end of the build (build-requires
  gets confused by executable files starting with """"): make the tests
  non-executable.

* Wed Nov 20 2002 Mihai Ibanescu <misa@redhat.com>
2.2.2-5
- Fixed configuration patch to add -lcrypt when compiling cryptmodule.c

2.2.2-4
- Spec file change from Matt Wilson <msw@redhat.com> to disable linking 
  with the C++ compiler.

* Mon Nov 11 2002 Mihai Ibanescu <misa@redhat.com>
2.2.2-3.*
- Merged patch from Karsten Hopp <karsten@redhat.de> from 2.2.1-17hammer to
  use %%{_libdir}
- Added XFree86-libs as BuildRequires (because of tkinter)
- Fixed duplicate listing of plat-linux2
- Fixed exclusion of lib-dynload/japanese
- Added lib64 patch for the japanese codecs
- Use setup magic instead of using tar directly on JapaneseCodecs

* Tue Nov  5 2002 Mihai Ibanescu <misa@redhat.com>
2.2.2-2
- Fix #76912 (python-tools contains idle, which uses tkinter, but there is no
  requirement of tkinter from python-tools).
- Fix #74013 (rpm is missing the /usr/lib/python2.2/test directory)

* Mon Nov  4 2002 Mihai Ibanescu <misa@redhat.com>
- builds as python2 require a different libdb
- changed the buildroot name of python to match python2 builds

* Fri Nov  1 2002 Mihai Ibanescu <misa@redhat.com>
- updated python to 2.2.2 and adjusted the patches accordingly

* Mon Oct 21 2002 Mihai Ibanescu <misa@redhat.com>
- Fix #53930 (Python-2.2.1-buildroot-bytecode.patch)
- Added BuildPrereq dependency on gcc-c++

* Fri Aug 30 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.1-17
- security fix for _execvpe

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
- added bin/python2.0 to files list (suggested by Martin v. L?)

* Tue Sep 26 2000 Jeremy Hylton <jeremy@beopen.com>
- updated for release 1 of 2.0b2
- use .bz2 version of Python source

* Tue Sep 12 2000 Jeremy Hylton <jeremy@beopen.com>
- Version 2 of 2.0b1
- Make the package relocatable.  Thanks to Suchandra Thapa.
- Exclude Tkinter from main RPM.  If it is in a separate RPM, it is
  easier to track Tk releases.
