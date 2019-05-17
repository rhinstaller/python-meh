PKGNAME=python-meh
VERSION=$(shell awk '/Version:/ { print $$2 }' $(PKGNAME).spec)
RELEASE=$(shell awk '/Release:/ { print $$2 }' $(PKGNAME).spec | sed -e 's|%.*$$||g')
TAG=r$(VERSION)-$(RELEASE)

PREFIX=/usr

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
	python setup.py -q clean --all

test:
	@echo "*** Running unittests ***"
	PYTHONPATH=. python $(TESTSUITE) -v

install:
	python setup.py install --root=$(DESTDIR)
	$(MAKE) -C po install

ChangeLog:
	(GIT_DIR=.git git log > .changelog.tmp && mv .changelog.tmp ChangeLog; rm -f .changelog.tmp) || (touch ChangeLog; echo 'git directory not found: installing possibly empty changelog.' >&2)

tag:
	git tag -a -m "Tag as $(TAG)" -f $(TAG)
	@echo "Tagged as $(TAG)"

archive: tag po-pull
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

local: po-pull
	@rm -f ChangeLog
	@make ChangeLog
	@rm -rf $(PKGNAME)-$(VERSION).tar.gz
	@rm -rf /tmp/$(PKGNAME)-$(VERSION) /tmp/$(PKGNAME)
	@dir=$$PWD; cp -a $$dir /tmp/$(PKGNAME)-$(VERSION)
	@cd /tmp/$(PKGNAME)-$(VERSION) ; python setup.py -q sdist
	@cp /tmp/$(PKGNAME)-$(VERSION)/dist/$(PKGNAME)-$(VERSION).tar.gz .
	@rm -rf /tmp/$(PKGNAME)-$(VERSION)
	@echo "The archive is in $(PKGNAME)-$(VERSION).tar.gz"

rpmlog:
	@git log --pretty="format:- %s (%ae)" $(TAG).. |sed -e 's/@.*)/)/'
	@echo

potfile:
	$(MAKE) -C po potfile

po-pull:
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
