#!/usr/bin/env python3
import os

class robot:
	def __init__(self):
		self.fitness=0.0
		self.path='default'

def main():
	#parser = argparse.ArgumentParser(description='Finds best phenotype.')
	#parser.add_argument('path', type=string, help='Path to files.')

	#args = parser.parse_args()
	
	bestrobot = robot()

	given_path='pyrevolve/tutorials/data/default_experiment/1/data_fullevolution/fitness'
	print(given_path)

	for path in os.listdir(given_path):
		full_path=os.path.join(given_path,path)
		if not os.path.isfile(full_path):
			print("Continuing")
			continue
		with open(full_path) as fitness_file:
			for fitness in fitness_file:
				if not fitness=="None":
					if float(fitness) > float(bestrobot.fitness):
						bestrobot.fitness=fitness
						bestrobot.path=path
	
	print("Best fitness from robot " + bestrobot.path + " with fitness " + bestrobot.fitness)


if __name__ == "__main__":
    main()
