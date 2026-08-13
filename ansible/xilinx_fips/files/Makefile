 
fips_override.so: fips_override.c
	gcc -Wall -O2 -fpic -shared -ldl -o $@ $^

clean:
	rm -f fips_override.so
