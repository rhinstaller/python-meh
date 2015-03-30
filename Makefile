PKGNAME=python-meh
VERSION=$(shell awk '/Version:/ { print $$2 }' $(PKGNAME).spec)
RELEASE=$(shell awk '/Release:/ { print $$2 }' $(PKGNAME).spec | sed -e 's|%.*$$||g')
TAG=r$(VERSION)-$(RELEASE)

PREFIX=/usr

PYTHON2=python2
PYTHON3=python3
PYTHON=$(PYTHON2)

TESTSUITE:=tests/baseclass.py

PYCHECKEROPTS=--no-argsused --no-miximport --maxargs 0 --no-local -\# 0 --only -Q

ZANATA_PULL_ARGS = --transdir po/
ZANATA_PUSH_ARGS = --srcdir po/ --push-type source --force

default: all

all:
	$(MAKE) -C po

clean:
	-rm *.tar.gz meh/*.pyc meh/ui/*.pyc tests/*.pyc ChangeLog
	$(MAKE) -C po clean
	$(PYTHON) setup.py -q clean --all

test:
	@echo "*** Running unittests with Python 2 ***"
	PYTHONPATH=. $(PYTHON2) $(TESTSUITE) -v

	@echo "*** Running unittests with Python 3 ***"
	PYTHONPATH=. $(PYTHON3) $(TESTSUITE) -v

install:
	$(PYTHON) setup.py install --root=$(DESTDIR)
	$(MAKE) -C po install

ChangeLog:
	(GIT_DIR=.git git log > .changelog.tmp && mv .changelog.tmp ChangeLog; rm -f .changelog.tmp) || (touch ChangeLog; echo 'git directory not found: installing possibly empty changelog.' >&2)

tag:
	git tag -a -m "Tag as $(TAG)" -f $(TAG)
	@echo "Tagged as $(TAG)"

archive: tag local

local: po-pull
	@rm -f ChangeLog
	@make ChangeLog
	git archive --format=tar --prefix=$(PKGNAME)-$(VERSION)/ $(TAG) > $(PKGNAME)-$(VERSION).tar
	mkdir -p $(PKGNAME)-$(VERSION)/po
	cp ChangeLog $(PKGNAME)-$(VERSION)/
	cp po/*.po $(PKGNAME)-$(VERSION)/po/
	tar -rf $(PKGNAME)-$(VERSION).tar $(PKGNAME)-$(VERSION)
	gzip -9 $(PKGNAME)-$(VERSION).tar
	rm -rf $(PKGNAME)-$(VERSION)
	@echo "The archive is in $(PKGNAME)-$(VERSION).tar.gz"

rpmlog:
	@git log --pretty="format:- %s (%ae)" $(TAG).. |sed -e 's/@.*)/)/'
	@echo

potfile:
	$(MAKE) -C po potfile

po-pull:
	rpm -q zanata-python-client &>/dev/null || ( echo "need to run: dnf install zanata-python-client"; exit 1 )
	zanata pull $(ZANATA_PULL_ARGS)

bumpver: potfile
	zanata push $(ZANATA_PUSH_ARGS) || ( echo "zanata push failed"; exit 1 )
	@NEWSUBVER=$$((`echo $(VERSION) |cut -d . -f 2` + 1)) ; \
	NEWVERSION=`echo $(VERSION).$$NEWSUBVER |cut -d . -f 1,3` ; \
	DATELINE="* `date "+%a %b %d %Y"` `git config user.name` <`git config user.email`> - $$NEWVERSION-1"  ; \
	cl=`grep -n %changelog python-meh.spec |cut -d : -f 1` ; \
	tail --lines=+$$(($$cl + 1)) python-meh.spec > speclog ; \
	(head -n $$cl python-meh.spec ; echo "$$DATELINE" ; make --quiet rpmlog 2>/dev/null ; echo ""; cat speclog) > python-meh.spec.new ; \
	mv python-meh.spec.new python-meh.spec ; rm -f speclog ; \
	sed -i "s/Version: $(VERSION)/Version: $$NEWVERSION/" python-meh.spec ; \
	sed -i "s/version='$(VERSION)'/version='$$NEWVERSION'/" setup.py

.PHONY: clean install tag archive local
