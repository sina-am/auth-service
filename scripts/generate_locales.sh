#!/bin/sh

if [ "$DOCKER_ENV" = true ]; then
    pygettext3 -d app -o locales/base.pot *
    msgfmt -o locales/en/LC_MESSAGES/base.mo locales/en/LC_MESSAGES/base
    msgfmt -o locales/fa/LC_MESSAGES/base.mo locales/fa/LC_MESSAGES/base

else
    /usr/lib/python3.10/Tools/i18n/pygettext.py -d app/models -o locales/base.pot *
    msgfmt -o locales/en/LC_MESSAGES/base.mo locales/en/LC_MESSAGES/base
    msgfmt -o locales/fa/LC_MESSAGES/base.mo locales/fa/LC_MESSAGES/base
fi