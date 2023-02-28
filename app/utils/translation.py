import gettext

_ = gettext.gettext

fa = gettext.translation('base', localedir='locales', languages=['fa'])
fa.install()
