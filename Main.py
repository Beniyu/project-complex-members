import matplotlib.pyplot as plt
from BridgeManager import BridgeManager


class Main:
    def __init__(self):
        # points = [[0,0], [815/3,0], [815*2/3,0], [815,0], [0,255], [815/3,255/3*2], [815/3*2,255/3]]
        points = [[0, 0], [271.61378659666667, 27.354229363193397], [543.3135521303334, 54.71711766668792], [815, 82.078664748], [0, 255], [471.1068880986666, 155.0436415503853]]
        connections = [[1,2], [2,3], [3,4], [5,6], [2,6], [3,6], [5,2],[6,4]]
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
        plt.ylim(0,300)
        plt.show()


instance = Main()
