import matplotlib.pyplot as plt
from BridgeManager import BridgeManager


class Main:
    def __init__(self):
        # points = [[0,0], [815/3,0], [815*2/3,0], [815,0], [0,255], [815/3,255/3*2], [815/3*2,255/3]]
        points = [[0, 0], [121.89484784300001, 33.94703816699998], [815, 106.592825656], [0, 255], [153.44106321000007, 252.544643003]]
        connections = [[1,2], [2,3], [4,5], [5,3], [4,2], [2,5]]
        constraints = {1: 'x', 4:'xy'}
        loads = [{3:[0,-1350*0.95,0]}, {3:[0,135*0.95,0]}]

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
