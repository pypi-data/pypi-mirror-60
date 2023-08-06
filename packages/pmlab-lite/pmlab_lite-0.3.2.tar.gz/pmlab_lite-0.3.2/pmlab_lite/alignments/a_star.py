from pmlab_lite.pn import PetriNet
from .alignment import Alignment
import variables as v
import numpy
import tqdm
import heapq
import tqdm

BLANK = '-' 
EPSILON = 0.00001


def Marking_vector(length, index_place, index_place_log):
	#creating a mark vector, of length = #places and fill unmarked 
	mark_vector =  list( numpy.repeat(0, length) )
	#marking the specified places in model/log
	mark_vector[index_place] = 1
	mark_vector[index_place_log] = 1
	
	return mark_vector

def Marking_updater(child_node, parent_node, incidence_matrix, transition_index):
	child_node.marking_vector = incidence_matrix[:,transition_index] + parent_node.marking_vector
	child_node.parent_node = parent_node


class A_star(Alignment):
	
	def __init__(self):
		Alignment.__init__(self)
		self.solutions = []
		
	#a star algorithm
	def A_star_exe(self, model_net, total_trace, heuristic_variant="matrix", no_of_solutions=1):
		
		v.solutions = dict() 

		#heuristic = Heuristic(heuristic_variant)
		
		for key in tqdm.tqdm(total_trace):
			trace = total_trace[key]				 # = ['t1', 't2', 't3']
			
			trace_net = PetriNet()
			trace_net.make_trace_net(trace)		
			
			sp_net = model_net.synchronous_product(trace_net)
			incidence_matrix = sp_net.incidence_matrix()
			places = list( sp_net.places.values() )
			transitions_by_index = sp_net.transitions_by_index()
			
			index_start_places = sp_net.get_index_initial_places()
			index_final_places = sp_net.get_index_final_places()
			index_place_start = index_start_places[0]
			index_place_end = index_final_places[0]
			index_place_start_log = index_start_places[1]
			index_place_end_log = index_final_places[1]	
			
			#creating inital marking vector
			init_mark_vector = Marking_vector(len(places), index_place_start, index_place_start_log)
			
			#creating final marking vector 
			final_mark_vector = Marking_vector(len(places), index_place_end, index_place_end_log)
			
			#storing the speciications of the Synchronous Product
			v.incidence_matrix = incidence_matrix
			v.init_mark_vector = init_mark_vector
			v.final_mark_vector = final_mark_vector
			
			#--initializing variables
			v.closed_list = closed_list = []
			v.open_list = open_list = []
			self.solutions = []
			self.fitness = []
			self.alignment_move = []
			self.move_in_model = []
			self.move_in_log = []
			self.fitness = []
			
			#creating initial node in the search space
			current_node = Node()
			current_node.marking_vector = numpy.array(init_mark_vector[:])
			current_node.observed_trace_remain = trace    
			current_node.Cost_to_final(transitions_by_index)
			open_list.append( [current_node.total_cost, current_node] )
			
			#iterating until open_list has no elements
			while len(open_list) > 0:
				# build min heap from open list
				heapq.heapify(open_list)					

				current_node = heapq.heappop(v.open_list)	#pop cheapest node from open list as (total cost, node)
				closed_list.append(current_node)			#append it to closed list as (total cost, node)
				current_node = current_node[1]				#make the current node just the node of the tuple
				
				#checking whether the node is a solution or not, then investigate
				if( numpy.array_equal( current_node.marking_vector, final_mark_vector) ):
					self.solutions.append(current_node)
					self.__Fitness()
					self.__Move_alignment()
					self.Move_in_model()
					self.Move_in_log()
					
					v.solutions[key] = self.alignment_move
					
					if len(self.solutions) >= no_of_solutions:
						break
				else:
					current_node.Investigate(incidence_matrix, transitions_by_index)
						
		return v.solutions
	
	def __Fitness(self):
		for sol in self.solutions:
			u = sol.alignment_up_to
			self.fitness.append( round ( len( [e for e in u if ((e[0]!='-' and e[1]!='-') or ('tau' in e[1])) ]) / len(u), 3) )
		
	def __Move_alignment(self):
		for sol in self.solutions:
			u = sol.alignment_up_to
			self.alignment_move.append( [e for e in u if ('tau' not in e[1])] )
		
	def Move_in_model(self):
		for sol in self.solutions:
			u = sol.alignment_up_to
			self.move_in_model.append( [e[1] for e in u if (e[1]!='-' and ('tau' not in e[1]))] )  	#false oder of e[i]
		
	def Move_in_log(self):
		for sol in self.solutions:
			u = sol.alignment_up_to
			self.move_in_log.append( [e[0] for e in u if e[0] != '-'])								#false order of e[i]


class Node():	
	def __init__(self):
		#shows a marking node
		self.marking_vector = []
		self.active_transitions = []
		self.parent_node = ''
		self.observed_trace_remain = []
		self.alignment_up_to = []			#it's of the form [ (t1,t1), (t2,-), (-,t3), ... ]
		
		self.cost_from_init_marking = 0 
		self.Cost_from_init()
		self.cost_to_final_marking = 1000
		self.total_cost = self.cost_from_init_marking + self.cost_to_final_marking
	
	#method for comparing two objects (python 3.7)
	def __lt__(self, other):
		return self.total_cost < other.total_cost
		
	#this funtion calls other functions to investigate the current node
	def Investigate(self, incidence_matrix, transitions_by_index):
		'''
		:param incidence_matrix: matrix of the synchronous product
		:param transitions by index: reverse of the dict 'net.transitions', to access transitions names by index
		'''
		
		#finding active transitions
		self.Find_active_transitions(incidence_matrix) #this is also done when finding the child nodes, so every node further investigated upon already has active t's found

		#heuristic evaluation of active transitions
		for i in self.active_transitions:
			#computing the distance of an active transition to the final marking (a place in case of WF net)
			self.Cost_to_final(transitions_by_index) #????? this has done before (double check)
			
			#make child node and update it's marking
			child_node = self.Make_child_node(incidence_matrix, i)
			move = str()

			# --Synchronous move--
			if transitions_by_index[i].endswith("synchronous"):
				
				#update it's remaining trace
				child_node.observed_trace_remain = self.observed_trace_remain[1:]
				child_node.alignment_up_to = self.alignment_up_to +  [ (self.observed_trace_remain[0], transitions_by_index[i][:-12] ) ]
				move = ",synchronous move,"
				
			# --Model       move--
			elif transitions_by_index[i].endswith("model"):
				
				#update it's remaining trace
				child_node.observed_trace_remain = self.observed_trace_remain[:]
				child_node.alignment_up_to = self.alignment_up_to + [ ('-', transitions_by_index[i][:-6] ) ]
				move = ",move in model,"
					
			# --Log         move--
			elif transitions_by_index[i].endswith("log"):

				#update it's remaining trace
				child_node.observed_trace_remain = self.observed_trace_remain[1:]
				child_node.alignment_up_to = self.alignment_up_to + [ (self.observed_trace_remain[0], '-') ]
				move = ",move in log,"

			#update it's cost
			child_node.Update_costs(transitions_by_index)
				
			#check whether it's in the closed list or it's a cheaper marking
			self.Add_node(v.open_list, v.closed_list, child_node, move)
			
	def Find_active_transitions(self, incidence_matrix):
		#looping over transitions of the synchronous product, to see which are active, given the marking of that node
		for i in range(0, incidence_matrix.shape[1]):											#im.shape[1] returns #columns = #transitions
			
			if numpy.all( (incidence_matrix[:, i] + self.marking_vector) >= 0 ):				#im[:,i] returns i-th column as list
				#transition i is active
				if i not in self.active_transitions:
					self.active_transitions.append(i)
					
	#deciding on whether or not to add a node to the open list
	def Add_node(self, open_list, closed_list, child_node, id):
		#checking whether it is in the closed list
		#ind is a list like [12,34,10]
		ind = [k for k in range( len(closed_list) ) if numpy.array_equal(child_node.marking_vector, closed_list[k][1].marking_vector) ]
		
		if len(ind) > 0:
			pass
		#checking whether it is in the open list, update if we found it
		else:
			ind = [k for k in range(len(open_list)) if numpy.array_equal(child_node.marking_vector, open_list[k][1].marking_vector)]
			
			#at least once in open list
			if ind:
				for k in ind:
					if open_list[k][1].cost_from_init_marking > child_node.cost_from_init_marking:			#that '<' was hard to find 
						open_list[k] = [child_node.total_cost, child_node]
					else: 
						continue
			#not in open list yet
			else:
				open_list.append( [child_node.total_cost, child_node] )

	def Make_child_node(self, incidence_matrix, i):
		child_node = Node()
		#updating the marking of the child node, i.e. the current marking after transition i was fired
		child_node.marking_vector = incidence_matrix[:, i] + self.marking_vector
		child_node.parent_node = self
		return child_node

	def Cost_from_init(self):
		self.cost_from_init_marking = 1*sum( [0 if ((x[0]!='-' and x[1]!='-') or ('tau' in x[1])) else 1 for x in self.alignment_up_to]) #+EPSILON

	#calcucalte the remaining cost to the final marking,based on a heuristic
	def Cost_to_final(self, transitions_by_index):
		b = numpy.array(v.final_mark_vector) - numpy.array(self.marking_vector) 	#marking vector is already array..?
		x = numpy.linalg.lstsq(v.incidence_matrix, b, rcond=None)[0]
		
		#rounding up or down, 
		x[x > 0] = 1
		x[x <= 0] = 0
		
		for key in transitions_by_index:
			if transitions_by_index[key].startswith('tau'):
				x[key] = 0
		
		self.cost_to_final_marking = numpy.sum(x)

	def Update_costs(self, transitions_by_index):
		self.Cost_from_init()
		self.Cost_to_final(transitions_by_index)	
		self.total_cost = self.cost_from_init_marking + self.cost_to_final_marking


class Heuristic():

	def __init__(self, variant):
		self.variant = variant

	def heuristic_to_final(self, incidence_matrix):
		if self.variant == "tl":
			self.remaining_trace_length_heursitic(incidence_matrix)
		elif self.variant == "lp":
			self.linear_programming_heursitic(incidence_matrix)
	
	def remaining_trace_length_heursitic(self, incidence_matrix):
		return True

	def linear_programming_heursitic(self, incidence_matrix):
		return True
