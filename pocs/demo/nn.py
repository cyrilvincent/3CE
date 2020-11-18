import sklearn.neighbors
import numpy as np
X = np.array([[-1, -1], [-2, -1], [-3, -2], [1, 1], [2, 1], [3, 2]])
model = sklearn.neighbors.NearestNeighbors(n_neighbors=6, algorithm='brute', leaf_size=30,)
#brute = o(DN²) kd_tree = o(DNLog(N)) pour D < 20, sinon ball_tree
fit = model.fit(X)
print(fit)
distances, indices = model.kneighbors(X)
print(indices)
print(distances)
distances, indices = model.kneighbors([[-1, -1]])
print(indices)
print(distances)
print(np.sqrt(np.abs(-1 - -2)**2 + np.abs(-1 - -1)**2))
print(np.sqrt(np.abs(-1 - -3)**2 + np.abs(-1 - -2)**2))
print(np.sqrt(np.abs(-1 - 1)**2 + np.abs(-1 - 1)**2))
print(np.sqrt(np.abs(-1 - 2)**2 + np.abs(-1 - 1)**2))
print(np.sqrt(np.abs(-1 - 3)**2 + np.abs(-1 - 2)**2))

#Pour une image il suffit d'effectuer
#CNN-BN | Flatten | CSV | NN
#ou VGG-BN | Flatten | CSV | NN
#ou MobileNET-BN | Flatten | CSV | NN
# En fait CNN-BN + Flatten donne une signature, ce qui est le m$eme concept que Hashing d'image ou Universal Sentence Encoder sauf que la taille du hash varie de 4096 à 25088

#https://codereview.stackexchange.com/questions/56367/k-nearest-neighbours-in-c-for-large-number-of-dimensions

#NN Image
#########

#OpenCV Flann
#Néssecite de s'entrainer sur les images à matcher
#Shazam for image https://medium.com/better-programming/shazam-for-paintings-a-computer-vision-project-513ff2e1b498

#Hashing d'image (recherche de copie)
#https://pypi.org/project/ImageHash/


#NN Text
#########

#Distance de Levenshtein (distance entre 2 textes)
#https://pypi.org/project/python-Levenshtein/0.12.0
#https://blog.sodifrance.fr/algorithme-de-levenshtein-en-c-net/
#https://www.nuget.org/packages/Fastenshtein/
#https://www.nuget.org/packages/String.Similarity/
#https://www.nuget.org/packages/NinjaNye.SearchExtensions.Levenshtein/


