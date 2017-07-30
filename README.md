# python-windows-service
Windows Service written on python

Problem, related to this code explained here:
https://stackoverflow.com/questions/45400594/windows-service-written-on-python-each-loop-increases-number-of-calls-by-one

Each iteration within internal loop the number of module calls that does the main job increases by one.
On the first iteration module is called one time, on the second - twice, on the third - thrice and so on...
