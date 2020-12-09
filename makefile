### this makefile needs to run first ". path.sh" to set an enviroment
default: human

human:
	python3 ./scripts/dicewars-human.py --ai dt.sdc dt.rand xlogin00 xlogin42
	
chalenge:
	python3 ./scripts/dicewars-human.py --ai dt.sdc dt.ste dt.stei dt.wpm_c
	
tournament: 
	mkdir -p ../tournaments
	mkdir -p ../logs
	python3 ./scripts/dicewars-tournament.py -r -g 2 -n 50 -b 101 -s 1337 -l ../logs --save ../tournaments/tournament-g2-n50.pickle
