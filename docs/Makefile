ARGPARSE_BASEARGS=--author 'Sarah Hoffmann' --author-email 'lonvia@denofr.de' --project-name pyosmium --url https://github.com/osmcode/pyosmium/
PYOSMIUM_VERSION=$(shell python3 -c 'import osmium.version;print(osmium.version.pyosmium_release)' | tail -n 1)

man:
	mkdir -p man
	argparse-manpage --module osmium.tools.pyosmium_get_changes --version '${PYOSMIUM_VERSION}' --function get_arg_parser ${ARGPARSE_BASEARGS} --output man/pyosmium-get-changes.1
	argparse-manpage --module osmium.tools.pyosmium_up_to_date --version '${PYOSMIUM_VERSION}' --function get_arg_parser ${ARGPARSE_BASEARGS} --output man/pyosmium-up-to-date.1

.PHONY: man
