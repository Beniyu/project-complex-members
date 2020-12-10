import matplotlib.pyplot as plt
from BridgeManager import BridgeManager


class Main:
    def __init__(self):
        # points = [[0,0], [815/3,0], [815*2/3,0], [815,0], [0,255], [815/3,255/3*2], [815/3*2,255/3]]
        #points = [[0, 0], [268.21560748666667, 34.98245362190765], [561.3312155243334, 73.212530015], [815, 73.212530015], [0, 255], [455.13652041666666, 194.78302994606088], [641.1618642743334, 170.17089258099995]]
        #points = [[0, 0], [265, 30], [490, 30], [815, 90], [0, 255], [410, 210]]
        #connections = [[1,2], [2,3], [3,4], [5,6], [6,4], [5,2], [2,6], [6,3]]
        points = [[0,0], [271,0], [543,0], [815,0], [0,255], [815/2,255/2]]
        connections = [[1,2],[2,3],[3,4],[5,6],[6,4],[5,2],[2,6],[6,3]]
        constraints = {1: 'x', 5:'xy'}
        loads = [{4:[0,-1320,0]}, {4:[0,132,0]}]
        bridge_manager = BridgeManager(points, connections, constraints, loads)
        self.instance = bridge_manager
        bridge_manager.display_points()
        bridge_manager.solve_tension()
        bridge_manager.draw_tensions()
        bridge_manager.get_member_properties_multi()
        print(bridge_manager.optimise_mass()[1])
        if hasattr(bridge_manager, 'final_members'):
            bridge_manager.draw_member_properties()
            bridge_manager.solve_extension()
            bridge_manager.get_reactions_2()
            bridge_manager.get_displacements()
            bridge_manager.draw_displacement()
        plt.plot(range(5))
        #plt.xlim(-100, 900)
        plt.ylim(-100, 350)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()


instance = Main()
