import numpy as np
import sys
import string
import argparse
import time
from collections import deque
import zmq
import matplotlib.pyplot as plt

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from django.conf import settings
from django.db import transaction

# 참조 path에 core를 추가하기 위함
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from core import models


capacity  = 32
FIG = 0

	
class Table:
	def get_ID(self, gps):
		GPS = (gps[0], gps[1])
		with transaction.atomic():
			centroid_queryset = models.CentroidTree.objects.filter(addressX=GPS[0], addressY=GPS[1])
			if len(centroid_queryset) <= 0:
				centroid = models.CentroidTree.objects.create(addressX=GPS[0], addressY=GPS[1])
			else:
				centroid = centroid_queryset.first()
		return centroid.id

	def get_GPS(self, ID):
		centroid_queryset = models.CentroidTree.objects.filter(id=ID)
		assert len(centroid_queryset) > 0, "GPS search: There is no place in DB"
		
		centroid = centroid_queryset.first()
		return (centroid.addressX, centroid.addressY)
	
	def reset_db(self):
		models.CentroidTreeWeight.objects.all().delete()
		models.CentroidTree.objects.all().delete()

table = Table()

class cluster:
	capacity = capacity 
	def __init__(self, init_point=None):
		self.R = 0
		if type(init_point) != type(None):
			self.centroid     = init_point
			self.N            = 1
			self.data         = np.array([init_point])
		else:
			self.centroid = None
			self.N			  = 0
			self.data         = np.array([])

	def is_fat(self):
		return self.N > self.capacity

	def get_radius(self):
		self.update()
		return self.R

	def get_centroid(self):
		self.update()
		return self.centroid

	def get_cluster(self):
		return self.data

	def get_scatter(self, fig=None):
		if fig == None:
			global FIG
			fig = FIG
			FIG +=1
		plt.figure(fig)
		plt.scatter(self.data[:,0],self.data[:,1])
		plt.show(block=False)

	def principal_axis(self):
		coords = self.data - self.centroid
		cov = np.cov(coords.T)
		evals, evecs = np.linalg.eig(cov)
		axis = np.argsort(evals)[::-1]
		return evecs[:,axis[0]]

	def split(self):
		new_cluster = cluster()
		vec = self.principal_axis()	
		div = np.dot(self.data - self.centroid,vec)

		new_cluster.data = self.data[ div>0 ]
		self.data = self.data[ div<=0 ]
		new_cluster.update()
		self.update()
		return new_cluster
	
	# NOT RECOVERABLE
	def split_into_bubble(self):
        # TODO: Tidy code structure
		output = [self]
		while True:
			done = True
			for c in output:
				if c.is_fat():
					done = False
					break

			if done: break

			for c in output:
				if c.is_fat():
					output.append(c.split())
		return output

	def update(self, R=True, C=True, N=True):
		if C:
			self.centroid = np.mean(self.data, axis=0)
		if R:
			d = np.sum(np.square(self.data-self.centroid),axis=1)
			self.R = max(d)
		if N:
			self.N = len(self.data)

	def add(self, point, R = True, C = True):
		if self.N == 0:
			self.data = np.array([point])
		else:
			self.data = np.append(self.data, [point], axis=0)
		self.update(R,C)
	
	def save(self):
		with transaction.atomic():
			node_ID = table.get_ID(self.centroid)
			from_centroid = models.CentroidTree.objects.get(id=node_ID)
			for p in self.data:
				p_ID = table.get_ID(p)
				to_centroid = models.CentroidTree.objects.get(id=p_ID)
				parent_centroid = models.CentroidTreeWeight.objects.create(
					from_centroid=from_centroid, to_centroid=to_centroid, is_real=True
				)
			

class K_CLUSTER:
	def __init__(self, k, data):
		self.k			= k
		self.data		= data
		self.DATA		= data
		self.cluster_list = []

	def is_fat(self):
		for c in self.cluster_list:
			if c.is_fat(): return True
		return False

	def get_clusters(self):
		return self.cluster_list

	def get_centroids(self):
		centroids = np.concatenate([[C.centroid] for C in self.cluster_list])
		return centroids

	def update(self):
		for c in self.cluster_list:
			c.update()

	def get_scatter(self, idx, fig=None):
		if fig==None: 
			global FIG
			fig = FIG
			FIG += 1

		for i, c in enumerate(self.cluster_list):
			if i not in idx: continue
			c.get_scatter(fig)
		plt.show(block=False)
		
	def closest(self, p):
		centroids = self.get_centroids()
		d =	np.sum(np.square(centroids-p),axis=1)
		return np.argmin(d)

	def initialize(self):
		p = self.data[0]
		self.data = np.delete(self.data, 0, 0)
		self.cluster_list.append(cluster(p))

		while len(self.cluster_list) < self.k:
			centroids = self.get_centroids()
			expanded_data = np.expand_dims(self.data, axis=1)
			expanded_centroids = np.expand_dims(centroids, axis=0)
			dist = np.square(expanded_data[:,:,0] - expanded_centroids[:,:,0]) + np.square(expanded_data[:,:,1] - expanded_centroids[:,:,1])

			min_dist = np.min(dist, axis=1)
			i = np.argmax(min_dist)
            
			self.cluster_list.append(cluster(self.data[i]))
			self.data = np.delete(self.data, i, 0)

	def k_means(self):
		for p in self.data:
			self.cluster_list[self.closest(p)].add(p)
		np.append(self.data, self.get_centroids(), axis=0)

	def k_means_advanced(self):
		centroids = self.get_centroids()

		new_cluster = [ cluster() for i in range(self.k) ]
		expanded_data = np.expand_dims(self.DATA, axis=1)
		expanded_centroids = np.expand_dims(centroids, axis=0)
		expanded_distance = np.square(expanded_data[:,:,0] - expanded_centroids[:,:,0]) + np.square(expanded_data[:,:,1] - expanded_centroids[:,:,1])

		for idx, d in enumerate(expanded_distance):
			new_cluster[np.argmin(d)].add(self.DATA[idx], R=False, C=False)

		self.cluster_list = new_cluster
		self.update()

class node:
	capacity = capacity
	def __init__(self, tier=0, end = False):
		self.tier 		= tier
		self.R		 	= 0
		self.end		= end
		self.centroid 	= None
		self.summary	= []
		self.child		= [] 

	def get_tier(self):
		return self.tier

	def get_centroid(self):
		self.update(R=False, C=True)
		return self.centroid

	def get_radius(self):
		update()
		return self.R

	def get_closest_node(self, GPS):
		if self.end: return -1
		d = np.sum(np.square(self.summary-GPS), axis=1)
		return np.argmin(d)

	def get_scatter(self, fig=None):
		if fig == None:
			global FIG
			fig = FIG
			FIG += 1

		if self.end:
			self.child.get_scatter(fig)
			plt.scatter(self.centroid[0], self.centroid[1],c='red')
		else:
			plt.figure(fig)
			plt.scatter(self.summary[:,0], self.summary[:,1],c='black')
			plt.scatter(self.centroid[0], self.centroid[1],c='red')
			plt.show(block=False)

	def print(self):
		for n in range(self.tier):
			print(' ',end='')
		print('Tier '+str(self.tier)+': '+str( len(self.child)))

	def print_hierchy(self):
		if self.end:
			for n in range(self.tier):
				print(' ',end='')
			print('-leaf: '+str(self.child.N))
		else:
			self.print()
			for node in self.child:
				node.print_hierchy()

	def is_fat(self):
		return len(self.child) > self.capacity

	def update(self, R=True, C=True):
		if self.end is False and len(self.child) == 1:
			self.end = self.child[0].end
			self.child = self.child[0].child
		
		if self.end:
			self.R = self.child.get_radius()
			self.centroid = self.child.get_centroid()
			return

		summary = []
		for n in self.child:
			if n.end:
				n.tier = self.tier+1
			summary.append([n.get_centroid()])
		self.summary = np.concatenate(summary)

		if C:
			self.centroid = np.mean(self.summary,axis=0)
		if R:
			d = np.sum(np.square(self.summary-self.centroid),axis=1)
			self.R = max(d)

	def add(self, child, update_flag=True):
		self.child.append(child)
		if update_flag:
			self.update()

	def principal_axis(self, data, centroid):
		coords = data - centroid
		cov = np.cov(coords.T)
		evals, evecs = np.linalg.eig(cov)
		axis = np.argsort(evals)[::-1]
		return evecs[:,axis[0]]

	def max_split(self):
		pool = [self.child]

		while len(pool) < capacity:
			L, R = [], []

			for n in pool:
				if len(n) <= 1: continue

                # CHANGE: concatenation part optimization
				data = np.concatenate([[nc.get_centroid()] for nc in n])

				center = np.mean(data,axis=0)
				vec = self.principal_axis(data, center)
				div = np.dot(data - center, vec)
				
				L_tmp, R_tmp = [], []
				for i, nc in enumerate(n):
					if div[i] >0: L_tmp.append(nc)
					else: R_tmp.append(nc)
				L.append(L_tmp)
				R.append(R_tmp)
			pool = L+R
		
		output = []
		for new_child in pool:
			n = node(self.tier+1)
			n.child = new_child
			output.append(n)

		self.child = output

	def expand(self):
		if self.end:
			return None

		if self.is_fat():
			self.max_split()

		return self.child

	def save(self):
		if self.end:
			self.child.save()
			return None
		else:
			with transaction.atomic():
				node_ID = table.get_ID(self.centroid)
				from_centroid = models.CentroidTree.objects.get(id=node_ID)
				for child in self.summary:
					child_ID = table.get_ID(child)
					to_centroid = models.CentroidTree.objects.get(id=child_ID)
					models.CentroidTreeWeight.objects.create(from_centroid=from_centroid, to_centroid=to_centroid, is_real=False)
			return self.child

class ClusterTree:
	def __init__(self,clusters=None):
		if clusters is not None:
			self.clusters = clusters
			self.cluster_list = clusters.cluster_list

	# return node
	def search_bubble(self, GPS):
		walker = self.head
		while not walker.end:
			idx = walker.get_closest_node(GPS)
			walker = walker.child[idx]
		return walker

	# return node
	def search_broad_bubble(self,GPS):
		walker = self.head
		while not walker.end:
			idx = walker.get_closest_node(GPS)
			prev = walker
			walker = walker.child[idx]
		return prev

	def request_nearest(self,GPS):
		n = self.search_bubble(GPS)
		return n.child.data
	
	def request_next_nearest(self,GPS,n):
		node = self.search_broad_bubble(GPS)
		n = min(n+1, len(node.child))
		d = np.sum(np.square(node.summary-GPS),axis=1)
		idx = np.argsort(d)
		output = np.concatenate([node.child[i].child.data for i in idx[:n]])
		return output

	def printTree(self):
		self.head.print_hierchy()

	def initTree(self):
		bubble_list = [c.split_into_bubble() for c in self.cluster_list]
		self.head = node(0)
		for bubble in bubble_list:
			T2_node = node(1)
			for b in bubble:
				n_leaf = node(end = True, tier = 2)
				n_leaf.child = b
				T2_node.add(n_leaf, update_flag=False)
			self.head.add(T2_node)	

	def buildTree(self):
		queue = deque([self.head])
		while queue:
			node = queue.popleft()
			child = node.expand()

			if child is not None:
				queue.extend(child)

	def updateTree(self):
		self.head.update(0)

	# only update target node (updateTree X) => need to updateTree to periodically
	def add(self,GPS):
		n = self.search_bubble(GPS)
		n.child.add(GPS)
		if n.child.is_fat():
			c1 = n.child
			c2 = c1.split()
			n1, n2 = node(tier=n.tier+1, end=True), node(tier=n.tier+1, end=True)
			n1.child, n2.child = c1, c2
			n.child, n.end = [n1, n2], False
			n.update()
			
	def saveTree(self):
		self.updateTree()

		queue = deque([self.head])
		while queue:
			node = queue.popleft()
			child = node.save()

			if child is not None:
				queue.extend(child)

	def loadTree(self):
		tree = {}
		leaf = set()
		
		with transaction.atomic():
			tree_queryset = models.CentroidTreeWeight.objects.all()

		for tree_info in tree_queryset:
			n_ID, c_ID, real = tree_info.from_centroid.id, tree_info.to_centroid.id, tree_info.is_real

			if real:
				new = table.get_GPS(c_ID)
				leaf.add(n_ID)
			else:
				new = node()
				new.centroid = c_ID

			if n_ID not in tree:
				tree[n_ID] = [ new ]
			else:
				tree[n_ID].append(new)

		self.head = node(0)
		self.head.centroid = min(tree.keys())

		queue = deque([self.head])

		while queue:
			n = queue.popleft()
			n_ID = n.centroid

			if n_ID in leaf:
				child = cluster()
				child.data = np.array(tree[n_ID])
				child.N = len(c.data)
				n.end = True
			else:
				child = tree[n_ID]
				queue.extend(tree[n_ID])

			n.child = child

def generate_data(N):
    ID_list = np.array([i for i in range(N)])
    GPS_list = np.random.rand(N, 2)
    return GPS_list, ID_list

if __name__=="__main__":
	k= 20
	N= 1000
	GPS_list, ID_list = generate_data(N)

	fig = [0, 1, 2]

	table.reset_db()

# K-MEANS clustering
	c = K_CLUSTER(k, GPS_list)
	c.initialize()
	c.k_means()
	c.get_scatter(range(k), fig[0])
	c.k_means_advanced()
	c.get_scatter(range(k), fig[1])

# Generate Cluster Tree
	CT = ClusterTree(c)
	CT.initTree()
	CT.buildTree()
	CT.updateTree()
	CT.printTree()

# Get neighbor data
	nearest = CT.request_nearest([0,0])
	print(nearest)
	#next_nearest = CT.request_next_nearest([0,0],2)
	#print(next_nearest)
	
# ADD new data to cluster tree
	CT.add([0,0])
	CT.updateTree()
	CT.search_broad_bubble([0,0]).get_scatter(fig[1])

# SAVE and LOAD	
	CT.saveTree()

	CT2 = ClusterTree()
	CT2.loadTree()
	CT2.updateTree()
	#CT2.printTree()

# Disply neighbor data
	
	startTime = time.time()

	CT2.search_bubble([0,0]).get_scatter(fig[2])
	CT2.search_bubble([0.5,0.5]).get_scatter(fig[2])

	for i in range(100):
		CT2.search_bubble(np.random.rand(2)).get_scatter(fig[2])

	endTime = time.time() - startTime
	print(endTime/10000)

	plt.show()

