protocol.py: protocol.yml protocol.py.template
	( \
  echo "# generated file, do not edit!"; \
  echo; \
  cat $@.template; \
  ./yml_to_py.py <$<; \
) >$@

clean:
	rm -f protocol.py
