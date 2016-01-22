# IM Status Python Plugin

plugin_in_files = autorate.rb-plugin.in
%.rb-plugin: %.rb-plugin.in $(INTLTOOL_MERGE) $(wildcard $(top_srcdir)/po/*po) ; $(INTLTOOL_MERGE) $(top_srcdir)/po $< $@ -d -u -c $(top_builddir)/po/.intltool-merge-cache

plugin_DATA = $(plugin_in_files:.rb-plugin.in=.rb-plugin)

plugindir = $(PLUGINDIR)/autorate
plugin_PYTHON = autorate/__init__.py	\
		autorate/AutorateConfigureDialog.py	

gtkbuilder_DATA =       \
                autorate-prefs.ui

gtkbuilderdir = $(plugindir)
EXTRA_DIST = $(plugin_in_files) $(plugin_PYTHON) $(gtkbuilder_DATA)
CLEANFILES = $(plugin_DATA)
DISTCLEANFILES = $(plugin_DATA)
