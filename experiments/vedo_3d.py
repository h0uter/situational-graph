import networkx as nx

pos = [[0.1, 2, 0.3],    [40, 0.5, -10],
       [0.1, -40, 0.3],  [-49, 0.1, 2],
       [10.3, 0.3, 0.4], [-109, 0.3, 50]]

ed_ls = [(x, y) for x, y in zip(range(0, 5), range(1, 6))]

G = nx.Graph()
G.add_edges_from(ed_ls)
nxpos = nx.spring_layout(G)
nxpts = [nxpos[pt] for pt in sorted(nxpos)]
# nx.draw(G, with_labels=True, pos=nxpos)
# plt.show()

raw_lines = [(pos[x],pos[y]) for x, y in ed_ls]
nx_lines = []
for x, y in ed_ls:
    p1 = nxpos[x].tolist() + [0] # add z-coord
    p2 = nxpos[y].tolist() + [0]
    nx_lines.append([p1,p2])

from vedo import *
raw_pts = Points(pos, r=12)
raw_edg = Lines(raw_lines).lw(2)
show(raw_pts, raw_edg, raw_pts.labels('id'),
     at=0, N=2, axes=True, sharecam=False)

nx_pts = Points(nxpts, r=12)
nx_edg = Lines(nx_lines).lw(2)
show(nx_pts, nx_edg, nx_pts.labels('id'),
     at=1, interactive=True)

write(nx_edg, 'afile.vtk') # save the lines