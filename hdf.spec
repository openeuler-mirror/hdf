Name: hdf
Version: 4.2.14
Release: 3
Summary: A general purpose library and file format for storing scientific data
License: IJG
URL: https://portal.hdfgroup.org/
Source0: https://support.hdfgroup.org/ftp/HDF/releases/HDF%{version}/src/%{name}-%{version}.tar.bz2
Patch0: hdf-4.2.5-maxavailfiles.patch
Patch1: hdf-ppc.patch
Patch2: hdf-4.2.4-sparc.patch
Patch3: hdf-s390.patch
Patch4: hdf-arm.patch
# Support DESTDIR in install-examples
Patch5: hdf-destdir.patch
# Install examples into the right location
Patch6: hdf-examplesdir.patch
# Add AArch64 definitions
Patch8: hdf-4.2.10-aarch64.patch
# ppc64le support
# https://bugzilla.redhat.com/show_bug.cgi?id=1134385
Patch9: hdf-ppc64le.patch

Patch10: add-riscv64-support.patch

# Fix syntax error on epel6 builds
# Use only if java is disabled
# Patch10: hdf-avoid_syntax_error_el6.patch

# For destdir/examplesdir patches
BuildRequires: automake, libtool, gcc, gcc-c++
BuildRequires: flex byacc libjpeg-devel zlib-devel %{!?el6:libaec-devel}
BuildRequires: libtirpc-devel
BuildRequires: gcc-gfortran, gcc

%description
HDF is a general purpose library and file format for storing scientific data.
HDF can store two primary objects: datasets and groups. A dataset is 
essentially a multidimensional array of data elements, and a group is a 
structure for organizing objects in an HDF file. Using these two basic 
objects, one can create and store almost any kind of scientific data 
structure, such as images, arrays of vectors, and structured and unstructured 
grids. You can also mix and match them in HDF files according to your needs.

%package devel
Summary: HDF development files
Provides: %{name}-static = %{version}-%{release}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: libjpeg-devel%{?_isa}
Requires: libtirpc-devel%{?_isa}
Requires: zlib-devel%{?_isa}

%description devel
HDF development headers and libraries.

%prep
%setup -q

%patch0 -p1 -b .maxavailfiles
%patch1 -p1 -b .ppc
%patch2 -p1 -b .sparc
%patch3 -p1 -b .s390
%patch4 -p1 -b .arm
%patch5 -p1 -b .destdir
%patch6 -p1 -b .examplesdir
%patch8 -p1 -b .aarch64
%patch9 -p1 -b .ppc64le
%patch10 -p1 -b .riscv64

find . -type f -name "*.h" -exec chmod 0644 '{}' \;
find . -type f -name "*.c" -exec chmod 0644 '{}' \;

# restore include file timestamps modified by patching
touch -c -r ./hdf/src/hdfi.h.ppc ./hdf/src/hdfi.h

%build

# For destdir/examplesdir patches
autoreconf -vif
# avoid upstream compiler flags settings
rm config/*linux-gnu
# TODO: upstream fix
# Shared libraries disabled: libmfhdf.so is not correctly compiled
# for missing link to libdf.so
export CFLAGS="%{optflags} -fPIC -I%{_includedir}/tirpc"
export LIBS="-ltirpc"
export FFLAGS="%{optflags} -fPIC -ffixed-line-length-none -fallow-argument-mismatch"
%configure --disable-production --disable-java --disable-netcdf \
 --enable-shared=no --enable-static=yes --enable-fortran %{!?el6:--with-szlib} \
 --includedir=%{_includedir}/%{name} --libdir=%{_libdir}/%{name}
%make_build

# correct the timestamps based on files used to generate the header files
touch -c -r hdf/src/hdf.inc hdf/src/hdf.f90
touch -c -r hdf/src/dffunc.inc hdf/src/dffunc.f90
touch -c -r mfhdf/fortran/mffunc.inc mfhdf/fortran/mffunc.f90
# netcdf fortran include need same treatement, but they are not shipped

%install
%make_install

install -pm 644 MANIFEST README.txt release_notes/*.txt %{buildroot}%{_pkgdocdir}/

rm -f %{buildroot}%{_libdir}/%{name}/*.la
rm -f %{buildroot}%{_libdir}/*.la

#Don't conflict with netcdf
for file in ncdump ncgen; do
  mv %{buildroot}%{_bindir}/$file %{buildroot}%{_bindir}/h$file
  # man pages are the same than netcdf ones
  rm %{buildroot}%{_mandir}/man1/${file}.1
done

# this is done to have the same timestamp on multiarch setups
touch -c -r README.txt %{buildroot}%{_includedir}/hdf/h4config.h

# Remove an autoconf conditional from the API that is unused and cause
# the API to be different on x86 and x86_64
pushd %{buildroot}%{_includedir}/hdf
grep -v 'H4_SIZEOF_INTP' h4config.h > h4config.h.tmp
touch -c -r h4config.h h4config.h.tmp
mv h4config.h.tmp h4config.h
popd

%check
make -j1 check

%files
%license COPYING
%{_pkgdocdir}/
%exclude %{_pkgdocdir}/examples
%{_bindir}/*
%{_mandir}/man1/*.gz

%files devel
%{_includedir}/%{name}/
%{_libdir}/%{name}/
%{_pkgdocdir}/examples/

%changelog
* Thu Nov 24 2022 misaka00251 <liuxin@iscas.ac.cn> - 4.2.14-3
- Add riscv64 support (Derived from federa project, thanks to fedora team)

* Tue Aug 10 2021 wangyue <wangyue92@huawei.com> - 4.2.14-2
- fix build error with gcc-10

* Web Feb 03 2021 yangshaoxing <yangshaoxing@uniontech> - 4.2.14-1
- Package init
