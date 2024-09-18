ARGPARSE_BASEARGS=--author 'Sarah Hoffmann' --author-email 'lonvia@denofr.de' --project-name pyosmium --url https://github.com/osmcode/pyosmium/

man:
	mkdir -p man
	argparse-manpage --pyfile ../tools/pyosmium-get-changes --function get_arg_parser ${ARGPARSE_BASEARGS} --output man/pyosmium-get-changes.1
	argparse-manpage --pyfile ../tools/pyosmium-up-to-date --function get_arg_parser ${ARGPARSE_BASEARGS} --output man/pyosmium-up-to-date.1

.PHONY: man
