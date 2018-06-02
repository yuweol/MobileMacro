import sys

from config import config
import distance

class miner():

	def __init__(self):
		pass

	def best_similarity(self, vectors):
		encoded = vectors.format_asc(0, vectors.size())
		return self.recursive_explore(0, len(encoded), encoded)
		
	def recursive_explore(self, start, end, target):
		if end - start < config.min_node:
			return None
	
		mid = int(((end - start) / 2) + start)
		if mid % 2 != 0:
			mid += 1
			
		left_target = target[start:mid]
		right_target = target[mid:end]
		
		print("calcaulting : (" + str(start) + " ~ " + str(mid) + " vs " + str(mid) + " ~ " + str(end) + ")")
		score = distance.nlevenshtein(left_target, right_target, method=2)
		cur_score = (score, start, end)
		
		left_score = self.recursive_explore(start, mid, target)
		right_score = self.recursive_explore(mid, end, target)
		
		top_score = None		
		if left_score == None and right_score == None:
			top_score = cur_score
		elif left_score == None:
			if cur_score[0] >= right_score[0]:
				top_score = cur_score
			else:
				top_score = right_score
		elif right_score == None:
			if cur_score[0] >= left_score[0]:
				top_score = cur_score
			else:
				top_score = left_score
		else:
			if cur_score[0] >= left_score[0]:
				top_score = cur_score
			else:
				top_score = left_score
				
			if top_score[0] == right_score[0]:
				if (right_score[2] - right_score[1]) > (top_score[2] - top_score[1]):
					top_score = right_score
			elif top_score[0] < right_score[0]:
				top_score = right_score
		
		print ("current score : " + str(cur_score[0]) + "(" + str(cur_score[1]) + " ~ " + str(cur_score[2]) + ")")
		if left_score != None:
			print ("left score : " + str(left_score[0]) + "(" + str(left_score[1]) + " ~ " + str(left_score[2]) + ")")
		if right_score != None:
			print ("right score : " + str(right_score[0]) + "(" + str(right_score[1]) + " ~ " + str(right_score[2]) + ")")
		print ("top score : " + str(top_score[0]) + "(" + str(top_score[1]) + " ~ " + str(top_score[2]) + ")")
		#a = input("press any key to continue")
		
		return top_score
