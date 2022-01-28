from knowledge_roadmap.entities.local_grid import LocalGrid

import pytest


def test_local_grid_init():
    lg = LocalGrid((0,0))
    assert lg.length_in_m == 3
    assert lg.cell_size_in_m == 0.003

def test_world_coord_in_local_grid():
    lg = LocalGrid((10,10), length_in_m=5)
    a = (10,10)
    assert lg.is_inside(a) == True

def test_world_coord_not_in_local_grid():
    lg = LocalGrid((10,10), length_in_m=5)
    a = (16,10)
    assert lg.is_inside(a) == False

def test_calc_length_num_cells():
    lg = LocalGrid((0,0), length_in_m=3, cell_size_in_m=0.003)
    assert lg.length_num_cells == 1000

def test_world_coord2cell_idxs():
    lg = LocalGrid((0,0), length_in_m=6)
    a = (-1.5,1.5)
    b = lg.world_coords2cell_idxs(a)
    assert lg.length_num_cells == 2000
    assert b == (500,1500)

def test_cell_idxs2world_coords():
    lg = LocalGrid((0,0), length_in_m=6)
    a = (500, 1500)
    b = lg.cell_idx2world_coords(a)
    assert b == pytest.approx((-1.5,1.5), 0.1)

def test_cell_idxs2world_coords_offcenter():
    lg = LocalGrid((1,1), length_in_m=3)
    a = (0,0) # cell idxs
    b = lg.cell_idx2world_coords(a)
    assert b == pytest.approx((-0.5,-0.5), 0.1)

def test_cell_idxs2world_coords_offcenter2():
    lg = LocalGrid((1,1), length_in_m=10, cell_size_in_m=0.1)
    a = (50,50) # cell idxs
    b = lg.cell_idx2world_coords(a)
    assert b == pytest.approx((1,1), 0.1)

def test_transformation_back_to_back():
    lg = LocalGrid((10,10), length_in_m=5)
    a = (10,10)
    b = lg.world_coords2cell_idxs(a)
    assert a == pytest.approx(lg.cell_idx2world_coords(b), 0.1)

    

# def test_derive_size_per_cell():
#     lg = LocalGrid((0,0), length_in_m=5)
#     assert lg.cell_size_in_m == pytest.approx(0.2, 0.1)