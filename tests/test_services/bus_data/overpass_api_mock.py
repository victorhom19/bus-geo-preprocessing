from overpy import Result, Node, Way, Relation, RelationMember, RelationNode, RelationWay


class OverpassApiMock:

    def __init__(self):
        self.data = None

    def load_empty(self):
        self.data = Result(elements=[])

    def load_base_stops(self):
        self.data = Result(elements=[
            Node(
                node_id=1,
                lat=60.00622072331832, lon=30.39055867084163,
                attributes={},
                tags={'name': 'Остановка 1', 'public_transport': 'platform'}
            ),
            Node(
                node_id=2,
                lat=60.00376370056657, lon=30.38813222581838,
                attributes={},
                tags={'name': 'Остановка 2', 'public_transport': 'platform'}
            ),
            Node(
                node_id=3,
                lat=59.99914841482375, lon=30.383509277515145,
                attributes={},
                tags={'name': 'Остановка 3', 'public_transport': 'platform'}
            )
        ])

    def load_base_routes(self):
        nodes_result = Result(elements=[
            # Платформы и места остановок
            Node(
                node_id=1,
                lat=60.00622072331832, lon=30.39055867084163,
                attributes={},
                tags={'name': 'Остановка 1 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=2,
                lat=60.00619192944939, lon=30.390657974053276,
                attributes={},
                tags={'name': 'Остановка 1 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=3,
                lat=60.00376370056657, lon=30.38813222581838,
                attributes={},
                tags={'name': 'Остановка 2 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=4,
                lat=60.00373961972188, lon=30.388225775206156,
                attributes={},
                tags={'name': 'Остановка 2 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=5,
                lat=59.99914841482375, lon=30.383509277515145,
                attributes={},
                tags={'name': 'Остановка 3 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=6,
                lat=59.99917930063261, lon=30.383649844706593,
                attributes={},
                tags={'name': 'Остановка 3 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=7,
                lat=59.995379586611435, lon=30.379569836337183,
                attributes={},
                tags={'name': 'Остановка 4 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=8,
                lat=59.995353683098266, lon=30.37974148249336,
                attributes={},
                tags={'name': 'Остановка 4 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=9,
                lat=59.996681687545596, lon=30.381510644086283,
                attributes={},
                tags={'name': 'Остановка 5 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=10,
                lat=59.99663103907874, lon=30.381371920731446,
                attributes={},
                tags={'name': 'Остановка 5 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=11,
                lat=59.99950398047311, lon=30.3842792584647,
                attributes={},
                tags={'name': 'Остановка 6 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=12,
                lat=59.99952046876944, lon=30.38422046913772,
                attributes={},
                tags={'name': 'Остановка 6 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=13,
                lat=60.00398890135085, lon=30.388806446091717,
                attributes={},
                tags={'name': 'Остановка 7 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=14,
                lat=60.00393001674256, lon=30.388645337486263,
                attributes={},
                tags={'name': 'Остановка 7 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=15,
                lat=60.006763924346444, lon=30.39163861366598,
                attributes={},
                tags={'name': 'Остановка 8 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=16,
                lat=60.00676804995057, lon=30.39156570043836,
                attributes={},
                tags={'name': 'Остановка 8 (место остановки)', 'public_transport': 'stop_position'}
            ),

            # Геометрия
            Node(
                node_id=17,
                lat=60.005152515822445, lon=30.38966032221969,
                attributes={},
                tags={}
            ),
            Node(
                node_id=18,
                lat=60.00385111220527, lon=30.388378394028454,
                attributes={},
                tags={'highway': 'crossing'}
            ),
            Node(
                node_id=19,
                lat=60.001735862880516, lon=30.386247559460816,
                attributes={},
                tags={'highway': 'crossing'}
            ),
            Node(
                node_id=20,
                lat=60.00161690848456, lon=30.386132323308424,
                attributes={},
                tags={'highway': 'traffic_signals'}
            ),
            Node(
                node_id=21,
                lat=60.0015138538511, lon=30.38603237425664,
                attributes={},
                tags={'highway': 'crossing'}
            ),
            Node(
                node_id=22,
                lat=60.00030840312693, lon=30.384815396515744,
                attributes={},
                tags={}
            ),
        ])

        routes_result = Result(elements=[
            Way(way_id=1, node_ids=[2, 17, 18, 4, 19, 20], tags={}, attributes={}, result=nodes_result),
            Way(way_id=2, node_ids=[20, 21, 22, 6, 8], tags={}, attributes={}, result=nodes_result),
            Way(way_id=3, node_ids=[10, 12, 14, 16], tags={}, attributes={}, result=nodes_result),

            Relation(rel_id=1, tags={'name': 'Маршрут 1'}, attributes={}, result=nodes_result, members=[
                RelationNode(ref=1, role='platform', attributes={}),
                RelationNode(ref=2, role='stop', attributes={}),
                RelationNode(ref=3, role='platform', attributes={}),
                RelationNode(ref=4, role='stop', attributes={}),
                RelationNode(ref=5, role='platform', attributes={}),
                RelationNode(ref=6, role='stop', attributes={}),
                RelationNode(ref=7, role='platform', attributes={}),
                RelationNode(ref=8, role='stop', attributes={}),
                RelationWay(ref=1, attributes={}),
                RelationWay(ref=2, attributes={})
            ]),

            Relation(rel_id=2, tags={'name': 'Маршрут 1'}, attributes={}, result=nodes_result, members=[
                RelationNode(ref=9, role='platform', attributes={}),
                RelationNode(ref=10, role='stop', attributes={}),
                RelationNode(ref=11, role='platform', attributes={}),
                RelationNode(ref=12, role='stop', attributes={}),
                RelationNode(ref=13, role='platform', attributes={}),
                RelationNode(ref=14, role='stop', attributes={}),
                RelationNode(ref=15, role='platform', attributes={}),
                RelationNode(ref=16, role='stop', attributes={}),
                RelationWay(ref=3, attributes={}),
            ])
        ])

        routes_result.expand(nodes_result)

        self.data = routes_result

    def load_complex_geometry_routes(self):
        nodes_result = Result(elements=[
            # Платформы и места остановок
            Node(
                node_id=1,
                lat=60.02363163473338, lon=30.408052838817227,
                attributes={},
                tags={'name': 'Остановка 1 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=2,
                lat=60.023630141832164, lon=30.408173442508275,
                attributes={},
                tags={'name': 'Остановка 1 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=3,
                lat=60.02028729344704, lon=30.40475337799373,
                attributes={},
                tags={'name': 'Остановка 2 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=4,
                lat=60.02024458875363, lon=30.404825414376155,
                attributes={},
                tags={'name': 'Остановка 2 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=5,
                lat=60.0147891931666, lon=30.389491867407045,
                attributes={},
                tags={'name': 'Остановка 3 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=6,
                lat=60.01483409579996, lon=30.389487461710093,
                attributes={},
                tags={'name': 'Остановка 3 (место остановки)', 'public_transport': 'stop_position'}
            ),

            # Геометрия
            Node(
                node_id=7,
                lat=60.021784116567304, lon=30.407417701936204,
                attributes={},
                tags={}
            ),
            Node(
                node_id=8,
                lat=60.022400293090094, lon=30.40707837137936,
                attributes={},
                tags={}
            ),
            Node(
                node_id=9,
                lat=60.02220393777795, lon=30.405917840380532,
                attributes={},
                tags={}
            ),
            Node(
                node_id=10,
                lat=60.021574511532094, lon=30.406274830564094,
                attributes={},
                tags={}
            ),
            Node(
                node_id=11,
                lat=60.01307576222848, lon=30.397743095183262,
                attributes={},
                tags={}
            ),
            Node(
                node_id=12,
                lat=60.0109073798413, lon=30.39551931073333,
                attributes={},
                tags={}
            ),
            Node(
                node_id=13,
                lat=60.01562694443312, lon=30.385617377542175,
                attributes={},
                tags={}
            ),
            Node(
                node_id=14,
                lat=60.01038679940976, lon=30.408481914366256,
                attributes={},
                tags={}
            )
        ])

        routes_result = Result(elements=[
            Way(way_id=1, node_ids=[2, 8], tags={}, attributes={}, result=nodes_result),
            Way(way_id=2, node_ids=[7, 8, 9, 10], tags={'junction': 'roundabout'}, attributes={}, result=nodes_result),
            Way(way_id=3, node_ids=[10, 4, 11, 12], tags={}, attributes={}, result=nodes_result),
            Way(way_id=4, node_ids=[13, 6, 11, 14], tags={}, attributes={}, result=nodes_result),

            Relation(rel_id=1, tags={'name': 'Маршрут 1'}, attributes={}, result=nodes_result, members=[
                RelationNode(ref=1, role='platform', attributes={}),
                RelationNode(ref=2, role='stop', attributes={}),
                RelationNode(ref=3, role='platform', attributes={}),
                RelationNode(ref=4, role='stop', attributes={}),
                RelationNode(ref=5, role='platform', attributes={}),
                RelationNode(ref=6, role='stop', attributes={}),
                RelationWay(ref=1, attributes={}),
                RelationWay(ref=2, attributes={}),
                RelationWay(ref=3, attributes={}),
                RelationWay(ref=4, attributes={})
            ]),
        ])

        routes_result.expand(nodes_result)

        self.data = routes_result

    def load_missing_data_routes(self):
        nodes_result = Result(elements=[
            # Платформы и места остановок
            Node(
                node_id=1,
                lat=60.00622072331832, lon=30.39055867084163,
                attributes={},
                tags={'name': 'Остановка 1 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=2,
                lat=60.00619192944939, lon=30.390657974053276,
                attributes={},
                tags={'name': 'Остановка 1 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=3,
                lat=60.00376370056657, lon=30.38813222581838,
                attributes={},
                tags={'name': 'Остановка 2 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=5,
                lat=59.99914841482375, lon=30.383509277515145,
                attributes={},
                tags={'name': 'Остановка 3 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=6,
                lat=59.99917930063261, lon=30.383649844706593,
                attributes={},
                tags={'name': 'Остановка 3 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=7,
                lat=59.995379586611435, lon=30.379569836337183,
                attributes={},
                tags={'name': 'Остановка 4 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=8,
                lat=59.995353683098266, lon=30.37974148249336,
                attributes={},
                tags={'name': 'Остановка 4 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=9,
                lat=59.996681687545596, lon=30.381510644086283,
                attributes={},
                tags={'name': 'Остановка 5 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=10,
                lat=59.99663103907874, lon=30.381371920731446,
                attributes={},
                tags={'name': 'Остановка 5 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=11,
                lat=59.99950398047311, lon=30.3842792584647,
                attributes={},
                tags={'name': 'Остановка 6 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=12,
                lat=59.99952046876944, lon=30.38422046913772,
                attributes={},
                tags={'name': 'Остановка 6 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=13,
                lat=60.00398890135085, lon=30.388806446091717,
                attributes={},
                tags={'name': 'Остановка 7 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=14,
                lat=60.00393001674256, lon=30.388645337486263,
                attributes={},
                tags={'name': 'Остановка 7 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=15,
                lat=60.006763924346444, lon=30.39163861366598,
                attributes={},
                tags={'name': 'Остановка 8 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=16,
                lat=60.00676804995057, lon=30.39156570043836,
                attributes={},
                tags={'name': 'Остановка 8 (место остановки)', 'public_transport': 'stop_position'}
            ),

            # Геометрия
            Node(
                node_id=17,
                lat=60.005152515822445, lon=30.38966032221969,
                attributes={},
                tags={}
            ),
            Node(
                node_id=18,
                lat=60.00385111220527, lon=30.388378394028454,
                attributes={},
                tags={'highway': 'crossing'}
            ),
            Node(
                node_id=19,
                lat=60.001735862880516, lon=30.386247559460816,
                attributes={},
                tags={'highway': 'crossing'}
            ),
            Node(
                node_id=20,
                lat=60.00161690848456, lon=30.386132323308424,
                attributes={},
                tags={'highway': 'traffic_signals'}
            ),
            Node(
                node_id=21,
                lat=60.0015138538511, lon=30.38603237425664,
                attributes={},
                tags={'highway': 'crossing'}
            ),
            Node(
                node_id=22,
                lat=60.00030840312693, lon=30.384815396515744,
                attributes={},
                tags={}
            ),
        ])

        routes_result = Result(elements=[
            Way(way_id=1, node_ids=[2, 17, 18, 19, 20], tags={}, attributes={}, result=nodes_result),
            Way(way_id=2, node_ids=[20, 21, 22, 6, 8], tags={}, attributes={}, result=nodes_result),
            Way(way_id=3, node_ids=[10, 12, 14, 16], tags={}, attributes={}, result=nodes_result),

            Relation(rel_id=1, tags={'name': 'Маршрут 1'}, attributes={}, result=nodes_result, members=[
                RelationNode(ref=1, role='platform', attributes={}),
                RelationNode(ref=2, role='stop', attributes={}),
                RelationNode(ref=3, role='platform', attributes={}),
                RelationNode(ref=5, role='platform', attributes={}),
                RelationNode(ref=7, role='platform', attributes={}),
                RelationNode(ref=8, role='stop', attributes={}),
                RelationWay(ref=1, attributes={}),
                RelationWay(ref=2, attributes={})
            ]),

            Relation(rel_id=2, tags={'name': 'Маршрут 1'}, attributes={}, result=nodes_result, members=[
                RelationNode(ref=9, role='platform', attributes={}),
                RelationNode(ref=10, role='stop', attributes={}),
                RelationNode(ref=11, role='platform', attributes={}),
                RelationNode(ref=12, role='stop', attributes={}),
                RelationNode(ref=13, role='platform', attributes={}),
                RelationNode(ref=14, role='stop', attributes={}),
                RelationNode(ref=15, role='platform', attributes={}),
                RelationNode(ref=16, role='stop', attributes={}),
                RelationWay(ref=3, attributes={}),
            ])
        ])

        routes_result.expand(nodes_result)

        self.data = routes_result

    def load_exceeding_routes(self):
        nodes_result = Result(elements=[
            # Платформы и места остановок
            Node(
                node_id=1,
                lat=60.00622072331832, lon=30.39055867084163,
                attributes={},
                tags={'name': 'Остановка 1 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=2,
                lat=60.00619192944939, lon=30.390657974053276,
                attributes={},
                tags={'name': 'Остановка 1 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=3,
                lat=60.00376370056657, lon=30.38813222581838,
                attributes={},
                tags={'name': 'Остановка 2 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=4,
                lat=60.00373961972188, lon=30.388225775206156,
                attributes={},
                tags={'name': 'Остановка 2 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=5,
                lat=59.99914841482375, lon=30.383509277515145,
                attributes={},
                tags={'name': 'Остановка 3 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=6,
                lat=59.99917930063261, lon=30.383649844706593,
                attributes={},
                tags={'name': 'Остановка 3 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=7,
                lat=59.995379586611435, lon=30.379569836337183,
                attributes={},
                tags={'name': 'Остановка 4 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=8,
                lat=59.995353683098266, lon=30.37974148249336,
                attributes={},
                tags={'name': 'Остановка 4 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=9,
                lat=59.996681687545596, lon=30.381510644086283,
                attributes={},
                tags={'name': 'Остановка 5 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=10,
                lat=59.99663103907874, lon=30.381371920731446,
                attributes={},
                tags={'name': 'Остановка 5 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=11,
                lat=59.99950398047311, lon=30.3842792584647,
                attributes={},
                tags={'name': 'Остановка 6 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=12,
                lat=59.99952046876944, lon=30.38422046913772,
                attributes={},
                tags={'name': 'Остановка 6 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=13,
                lat=60.00398890135085, lon=30.388806446091717,
                attributes={},
                tags={'name': 'Остановка 7 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=14,
                lat=60.00393001674256, lon=30.388645337486263,
                attributes={},
                tags={'name': 'Остановка 7 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=15,
                lat=60.006763924346444, lon=30.39163861366598,
                attributes={},
                tags={'name': 'Остановка 8 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=16,
                lat=60.00676804995057, lon=30.39156570043836,
                attributes={},
                tags={'name': 'Остановка 8 (место остановки)', 'public_transport': 'stop_position'}
            ),

            # Геометрия
            Node(
                node_id=17,
                lat=60.005152515822445, lon=30.38966032221969,
                attributes={},
                tags={}
            ),
            Node(
                node_id=18,
                lat=60.00385111220527, lon=30.388378394028454,
                attributes={},
                tags={'highway': 'crossing'}
            ),
            Node(
                node_id=19,
                lat=60.001735862880516, lon=30.386247559460816,
                attributes={},
                tags={'highway': 'crossing'}
            ),
            Node(
                node_id=20,
                lat=60.00161690848456, lon=30.386132323308424,
                attributes={},
                tags={'highway': 'traffic_signals'}
            ),
            Node(
                node_id=21,
                lat=60.0015138538511, lon=30.38603237425664,
                attributes={},
                tags={'highway': 'crossing'}
            ),
            Node(
                node_id=22,
                lat=60.00030840312693, lon=30.384815396515744,
                attributes={},
                tags={}
            ),
        ])

        routes_result = Result(elements=[
            Way(way_id=1, node_ids=[2, 17, 18, 4, 19, 20], tags={}, attributes={}, result=nodes_result),
            Way(way_id=2, node_ids=[20, 21, 22, 6, 8], tags={}, attributes={}, result=nodes_result),
            Way(way_id=3, node_ids=[10, 12, 14, 16], tags={}, attributes={}, result=nodes_result),

            Relation(rel_id=1, tags={'name': 'Маршрут 1'}, attributes={}, result=nodes_result, members=[
                RelationNode(ref=1, role='platform', attributes={}),
                RelationNode(ref=2, role='stop', attributes={}),
                RelationNode(ref=3, role='platform', attributes={}),
                RelationNode(ref=4, role='stop', attributes={}),
                RelationNode(ref=5, role='platform', attributes={}),
                RelationNode(ref=6, role='stop', attributes={}),
                RelationNode(ref=7, role='platform', attributes={}),
                RelationNode(ref=8, role='stop', attributes={}),
                RelationWay(ref=1, attributes={}),
                RelationWay(ref=2, attributes={})
            ]),

            Relation(rel_id=2, tags={'name': 'Маршрут 1'}, attributes={}, result=nodes_result, members=[
                RelationNode(ref=9, role='platform', attributes={}),
                RelationNode(ref=10, role='stop', attributes={}),
                RelationNode(ref=11, role='platform', attributes={}),
                RelationNode(ref=12, role='stop', attributes={}),
                RelationNode(ref=13, role='platform', attributes={}),
                RelationNode(ref=14, role='stop', attributes={}),
                RelationNode(ref=15, role='platform', attributes={}),
                RelationNode(ref=16, role='stop', attributes={}),
                RelationWay(ref=3, attributes={}),
            ])
        ])

        routes_result.expand(nodes_result)

        self.data = routes_result

    def load_bad_routes(self):
        nodes_result = Result(elements=[
            # Платформы и места остановок
            Node(
                node_id=1,
                lat=60.00622072331832, lon=30.39055867084163,
                attributes={},
                tags={'name': 'Остановка 1 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=2,
                lat=60.00619192944939, lon=30.390657974053276,
                attributes={},
                tags={'name': 'Остановка 1 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=3,
                lat=60.00376370056657, lon=30.38813222581838,
                attributes={},
                tags={'name': 'Остановка 2 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=4,
                lat=60.00373961972188, lon=30.388225775206156,
                attributes={},
                tags={'name': 'Остановка 2 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=5,
                lat=59.99914841482375, lon=30.383509277515145,
                attributes={},
                tags={'name': 'Остановка 3 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=6,
                lat=59.99917930063261, lon=30.383649844706593,
                attributes={},
                tags={'name': 'Остановка 3 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=7,
                lat=59.995379586611435, lon=30.379569836337183,
                attributes={},
                tags={'name': 'Остановка 4 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=8,
                lat=59.995353683098266, lon=30.37974148249336,
                attributes={},
                tags={'name': 'Остановка 4 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=9,
                lat=59.996681687545596, lon=30.381510644086283,
                attributes={},
                tags={'name': 'Остановка 5 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=10,
                lat=59.99663103907874, lon=30.381371920731446,
                attributes={},
                tags={'name': 'Остановка 5 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=11,
                lat=59.99950398047311, lon=30.3842792584647,
                attributes={},
                tags={'name': 'Остановка 6 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=12,
                lat=59.99952046876944, lon=30.38422046913772,
                attributes={},
                tags={'name': 'Остановка 6 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=13,
                lat=60.00398890135085, lon=30.388806446091717,
                attributes={},
                tags={'name': 'Остановка 7 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=14,
                lat=60.00393001674256, lon=30.388645337486263,
                attributes={},
                tags={'name': 'Остановка 7 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=15,
                lat=60.006763924346444, lon=30.39163861366598,
                attributes={},
                tags={'name': 'Остановка 8 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=16,
                lat=60.00676804995057, lon=30.39156570043836,
                attributes={},
                tags={'name': 'Остановка 8 (место остановки)', 'public_transport': 'stop_position'}
            ),

            # Геометрия
            Node(
                node_id=17,
                lat=60.005152515822445, lon=30.38966032221969,
                attributes={},
                tags={}
            ),
            Node(
                node_id=18,
                lat=60.00385111220527, lon=30.388378394028454,
                attributes={},
                tags={'highway': 'crossing'}
            ),
            Node(
                node_id=19,
                lat=60.001735862880516, lon=30.386247559460816,
                attributes={},
                tags={'highway': 'crossing'}
            ),
            Node(
                node_id=20,
                lat=60.00161690848456, lon=30.386132323308424,
                attributes={},
                tags={'highway': 'traffic_signals'}
            ),
            Node(
                node_id=21,
                lat=60.0015138538511, lon=30.38603237425664,
                attributes={},
                tags={'highway': 'crossing'}
            ),
            Node(
                node_id=22,
                lat=60.00030840312693, lon=30.384815396515744,
                attributes={},
                tags={}
            ),
        ])

        routes_result = Result(elements=[
            Way(way_id=1, node_ids=[2, 17, 18, 4, 19, 20], tags={}, attributes={}, result=nodes_result),
            Way(way_id=2, node_ids=[20, 21, 22, 6, 8], tags={}, attributes={}, result=nodes_result),
            Way(way_id=3, node_ids=[10, 12, 14, 16], tags={}, attributes={}, result=nodes_result),

            Relation(rel_id=1, tags={'name': 'Маршрут 1'}, attributes={}, result=nodes_result, members=[
                RelationNode(ref=1, role='platform', attributes={}),
                RelationNode(ref=2, role='stop', attributes={}),
                RelationNode(ref=3, role='platform', attributes={}),
                RelationNode(ref=4, role='stop', attributes={}),
                RelationNode(ref=5, role='platform', attributes={}),
                RelationNode(ref=6, role='stop', attributes={}),
                RelationNode(ref=7, role='platform', attributes={}),
                RelationNode(ref=8, role='stop', attributes={}),
                RelationWay(ref=1, attributes={}),
                RelationWay(ref=2, attributes={})
            ]),

            Relation(rel_id=2, tags={'name': 'Маршрут 1'}, attributes={}, result=nodes_result, members=[
                RelationNode(ref=9, role='platform', attributes={}),
                RelationNode(ref=10, role='stop', attributes={}),
                RelationWay(ref=3, attributes={}),
            ])
        ])

        routes_result.expand(nodes_result)

        self.data = routes_result

    def load_base_routes_reversed(self):
        nodes_result = Result(elements=[
            # Платформы и места остановок
            Node(
                node_id=1,
                lat=60.00622072331832, lon=30.39055867084163,
                attributes={},
                tags={'name': 'Остановка 1 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=2,
                lat=60.00619192944939, lon=30.390657974053276,
                attributes={},
                tags={'name': 'Остановка 1 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=3,
                lat=60.00376370056657, lon=30.38813222581838,
                attributes={},
                tags={'name': 'Остановка 2 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=4,
                lat=60.00373961972188, lon=30.388225775206156,
                attributes={},
                tags={'name': 'Остановка 2 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=5,
                lat=59.99914841482375, lon=30.383509277515145,
                attributes={},
                tags={'name': 'Остановка 3 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=6,
                lat=59.99917930063261, lon=30.383649844706593,
                attributes={},
                tags={'name': 'Остановка 3 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=7,
                lat=59.995379586611435, lon=30.379569836337183,
                attributes={},
                tags={'name': 'Остановка 4 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=8,
                lat=59.995353683098266, lon=30.37974148249336,
                attributes={},
                tags={'name': 'Остановка 4 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=9,
                lat=59.996681687545596, lon=30.381510644086283,
                attributes={},
                tags={'name': 'Остановка 5 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=10,
                lat=59.99663103907874, lon=30.381371920731446,
                attributes={},
                tags={'name': 'Остановка 5 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=11,
                lat=59.99950398047311, lon=30.3842792584647,
                attributes={},
                tags={'name': 'Остановка 6 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=12,
                lat=59.99952046876944, lon=30.38422046913772,
                attributes={},
                tags={'name': 'Остановка 6 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=13,
                lat=60.00398890135085, lon=30.388806446091717,
                attributes={},
                tags={'name': 'Остановка 7 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=14,
                lat=60.00393001674256, lon=30.388645337486263,
                attributes={},
                tags={'name': 'Остановка 7 (место остановки)', 'public_transport': 'stop_position'}
            ),
            Node(
                node_id=15,
                lat=60.006763924346444, lon=30.39163861366598,
                attributes={},
                tags={'name': 'Остановка 8 (платформа)', 'public_transport': 'platform'}
            ),
            Node(
                node_id=16,
                lat=60.00676804995057, lon=30.39156570043836,
                attributes={},
                tags={'name': 'Остановка 8 (место остановки)', 'public_transport': 'stop_position'}
            ),

            # Геометрия
            Node(
                node_id=17,
                lat=60.005152515822445, lon=30.38966032221969,
                attributes={},
                tags={}
            ),
            Node(
                node_id=18,
                lat=60.00385111220527, lon=30.388378394028454,
                attributes={},
                tags={'highway': 'crossing'}
            ),
            Node(
                node_id=19,
                lat=60.001735862880516, lon=30.386247559460816,
                attributes={},
                tags={'highway': 'crossing'}
            ),
            Node(
                node_id=20,
                lat=60.00161690848456, lon=30.386132323308424,
                attributes={},
                tags={'highway': 'traffic_signals'}
            ),
            Node(
                node_id=21,
                lat=60.0015138538511, lon=30.38603237425664,
                attributes={},
                tags={'highway': 'crossing'}
            ),
            Node(
                node_id=22,
                lat=60.00030840312693, lon=30.384815396515744,
                attributes={},
                tags={}
            ),
        ])

        routes_result = Result(elements=[
            Way(way_id=1, node_ids=[2, 17, 18, 4, 19, 20], tags={}, attributes={}, result=nodes_result),
            Way(way_id=2, node_ids=[20, 21, 22, 6, 8], tags={}, attributes={}, result=nodes_result),
            Way(way_id=3, node_ids=[10, 12, 14, 16], tags={}, attributes={}, result=nodes_result),

            Relation(rel_id=2, tags={'name': 'Маршрут 1'}, attributes={}, result=nodes_result, members=[
                RelationNode(ref=9, role='platform', attributes={}),
                RelationNode(ref=10, role='stop', attributes={}),
                RelationNode(ref=11, role='platform', attributes={}),
                RelationNode(ref=12, role='stop', attributes={}),
                RelationNode(ref=13, role='platform', attributes={}),
                RelationNode(ref=14, role='stop', attributes={}),
                RelationNode(ref=15, role='platform', attributes={}),
                RelationNode(ref=16, role='stop', attributes={}),
                RelationWay(ref=3, attributes={}),
            ]),

            Relation(rel_id=1, tags={'name': 'Маршрут 1'}, attributes={}, result=nodes_result, members=[
                RelationNode(ref=1, role='platform', attributes={}),
                RelationNode(ref=2, role='stop', attributes={}),
                RelationNode(ref=3, role='platform', attributes={}),
                RelationNode(ref=4, role='stop', attributes={}),
                RelationNode(ref=5, role='platform', attributes={}),
                RelationNode(ref=6, role='stop', attributes={}),
                RelationNode(ref=7, role='platform', attributes={}),
                RelationNode(ref=8, role='stop', attributes={}),
                RelationWay(ref=1, attributes={}),
                RelationWay(ref=2, attributes={})
            ]),
        ])

        routes_result.expand(nodes_result)

        self.data = routes_result

    def query(self, *args, **kwargs):
        return self.data
