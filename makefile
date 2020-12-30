### this makefile needs to run first ". path.sh" to set an enviroment
default: human

human:
	python3 ./scripts/dicewars-human.py --ai dt.sdc xrysav27 xlogin00 xlogin42
	
chalenge:
	python3 ./scripts/dicewars-human.py --ai dt.sdc dt.ste dt.stei dt.wpm_c
	
tournament: 
	mkdir -p ../tournaments
	mkdir -p ../logs
	python3 ./scripts/dicewars-tournament.py -r -g 4 -n 10 -l ../logs --save ../tournaments/tournament-g2-n50.pickle
	
tournament50: 
	mkdir -p ../tournaments
	mkdir -p ../logs
	python3 ./scripts/dicewars-tournament.py -r -g 4 -n 50 -l ../logs --save ../tournaments/tournament-g2-n50.pickle
	
tournament_test: 
	mkdir -p ../tournaments
	mkdir -p ../logs
	python3 ./scripts/dicewars-tournament.py -r -g 4 -n 10 -l ../logs --save ../tournaments/tournament-g2-n50.pickle --ai-under-test xrysav27
	
ai:
	python3 ./scripts/dicewars-ai-only.py -r -b 11 -o 22 -s 33 -c 44 -n 10 -l ../logs --ai dt.stei xlogin42
	
duel20:
	python3 ./scripts/dicewars-ai-only.py -r -n 20 --ai dt.ste xrysav27

duel20First:
	python3 ./scripts/dicewars-ai-only.py -r -n 20 --ai xrysav27 dt.ste
	
duel:
	python3 ./scripts/dicewars-ai-only.py -r -n 1 --ai dt.ste xrysav27

debugDuel:
	python3 ./scripts/dicewars-ai-only.py -r -n 1 --ai dt.ste xrysav27 --logdir ./

debugThreePlayers:
	python3 ./scripts/dicewars-ai-only.py -r -n 1 --ai dt.ste xrysav27 dt.stei --logdir ./

debugFourPlayers:
	python3 ./scripts/dicewars-ai-only.py -r -n 1 --ai dt.ste xrysav27 dt.stei xlogin00 --logdir ./

debugDuelFirst:
	python3 ./scripts/dicewars-ai-only.py -r -n 1 --ai xrysav27 dt.ste --logdir ./
