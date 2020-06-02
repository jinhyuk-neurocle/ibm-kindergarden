import numpy as np
import string
import argparse
import matplotlib.pyplot as plt

class cluster:
    def __init__(self, init_point=[0,0]):
        self.centroid     = init_point
        self.N             = 1
        self.data        = np.array([init_point])
        self.R            = 0

    def get_cluster(self):
        return self.data

    def update_radius(self):# to implement for tree
        for p in self.data:
            print(p)

    def update_centroid(self):
        self.centroid = np.mean(self.data, axis=0)

    def add(self, point):
        self.N += 1
        self.data = np.append(self.data, [point], axis=0)
        self.update_centroid()

class K_CLUSTER:
    fig = 0

    def __init__(self, k, data):
        self.k         = k
        self.data     = data
        self.cluster_list = []

    def get_clusters(self):
        return self.cluster_list

    def get_centroids(self):
        centroids = [[0,0]]
        for C in self.cluster_list:
            centroids = np.append(centroids, [C.centroid], axis=0)
        return centroids[1:]

    def display(self):
        plt.show()

    def get_scatter(self):
        plt.figure(self.fig)
        self.fig += 1
        for c in self.cluster_list:
            data = c.get_cluster()
            plt.scatter(data[:,0],data[:,1])
        plt.show(block=False)
        return self.fig-1

    def closest(self, p):
        d = []
        for C in self.cluster_list:
            d.append(D2(p,C.centroid))
        return d.index(min(d))

    # use k-center
    def initialize(self):
        p, self.data = pop(0,self.data)
        self.cluster_list.append(cluster(p))

        while len(self.cluster_list) < self.k:

            centroids = self.get_centroids()
            expanded_data = np.expand_dims(self.data, axis=1)
            expanded_centroids = np.expand_dims(centroids, axis=0)
            dist = np.square(expanded_data[:,:,0] - expanded_centroids[:,:,0]) + np.square(expanded_data[:,:,1] - expanded_centroids[:,:,1])

            min_dist = np.min(dist, axis=1)
            i = np.argmax(min_dist)
            
            p, self.data = pop(i, self.data)
            self.cluster_list.append(cluster(p))

    def k_means(self):
        for p in self.data:
            self.cluster_list[self.closest(p)].add(p)
        np.append(self.data, self.get_centroids(), axis=0)

    def k_means_advanced(self):
        centroids = self.get_centroids()
        new_cluster = [ cluster() for i in range(self.k) ]

        expanded_data = np.expand_dims(self.data, axis=1)
        expanded_centroids = np.expand_dims(centroids, axis=0)
        expanded_distance = np.square(expanded_data[:,:,0] - expanded_centroids[:,:,0]) + np.square(expanded_data[:,:,1] - expanded_centroids[:,:,1])

        for idx, d in enumerate(expanded_distance):
            new_cluster[np.argmin(d)].add(self.data[idx])
        for c in new_cluster:
            c.data = np.delete(c.data,0,0)
        self.cluster_list = new_cluster

def D2(p1, p2):
    return np.sum( (p1-p2)**2 )

def pop(i, data):
    return (data[i], np.delete(data, i , 0))

def generate_data(N):
    ID_list = np.array([i for i in range(N)])
    GPS_list = np.random.rand(N, 2)

    return GPS_list, ID_list

if __name__=="__main__":
    GPS_list, ID_list = generate_data(100000)
    c = K_CLUSTER(30, GPS_list)
    c.initialize()
    c.k_means()
    print(c.get_centroids())
    c.get_scatter()
    c.k_means_advanced()
    c.get_scatter()
    c.display()
