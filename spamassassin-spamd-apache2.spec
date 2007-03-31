#
# Conditional build:
%bcond_without	tests		# perform "make test"
#
%include	/usr/lib/rpm/macros.perl
%define	apxs	%{sbindir}/apxs
Summary:	spamd-apache2 - daemonized version of spamassassin as Apache2 module
Summary(pl.UTF-8):	spamd-apache2 - spamassassin w postaci demona jako moduł Apache2
Name:		spamassassin-spamd-apache2
Version:	3.1.8
Release:	0.1
License:	Apache Software License v2
Group:		Applications/Mail
Source0:	http://www.fnord.pl/spamd-apache2-%{version}.tar.bz2
# Source0-md5:	9f7724390e81a44877f2d980461bdee8
Source1:	%{name}.sysconfig
Source2:	%{name}.init
URL:		http://spamassassin.apache.org/
BuildRequires:	apache-apxs
BuildRequires:	apache-mod_perl >= 1:2
BuildRequires:	perl-Apache-Test >= 1:1.29
BuildRequires:	perl-Mail-SpamAssassin >= 3.001
BuildRequires:	perl-devel >= 1:5.8.0
BuildRequires:	rpmbuild(macros) >= 1.310
BuildRequires:	rpm-perlprov >= 4.1-13
%if %{with tests}
BuildRequires:	apache-base
%endif
Requires:	perl-Mail-SpamAssassin >= %{version}-%{release}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This distribution contains a mod_perl2 module, implementing the spamd
protocol from the SpamAssassin (http://spamassassin.apache.org/)
project in Apache2. It's mostly compatible with the original spamd.

%description -l pl.UTF-8
Ten pakiet zawiera moduł mod_perl2, implementujący protokół spamd z
projektu SpamAssassin (http://spamassassin.apache.org/) dla Apache'a
2. Jest w większości kompatybilny z oryginalnym spamd.

%prep
%setup -q -n spamd-apache2-%{version}

%build
%{__perl} Makefile.PL \
	INSTALLDIRS=vendor
%{__make}

%if %{with tests}
%{__make} test \
	APACHE_TEST_HTTPD=%{_sbindir}/httpd.prefork \
	APACHE_TEST_APXS=%{apxs}
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{sysconfig,rc.d/init.d},%{_sysconfdir}/mail/spamassassin}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/sysconfig/spamd-apache2
install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/spamd-apache2
touch $RPM_BUILD_ROOT%{_sysconfdir}/mail/spamassassin/spamd-apache2.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add spamd-apache2
%service spamd-apache2 restart

%preun
if [ "$1" = "0" ]; then
	%service spamd-apache2 stop
	/sbin/chkconfig --del spamd-apache2
fi

%files
%defattr(644,root,root,755)
%doc README.apache
%attr(755,root,root) %{_bindir}/*
%{perl_vendorlib}/Mail/SpamAssassin/*.pm
%{perl_vendorlib}/Mail/SpamAssassin/Spamd
%{_mandir}/man1/*
%{_mandir}/man3/*

%attr(754,root,root) /etc/rc.d/init.d/spamd-apache2
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/spamd-apache2
# XXX: ghost or config?
%ghost %attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/mail/spamassassin/spamd-apache2.conf
