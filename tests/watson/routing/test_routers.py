# -*- coding: utf-8 -*-
from watson.routing import routers
from pytest import raises
from tests.watson.routing.support import sample_request


class TestDict(object):
    def test_create(self):
        router = routers.Dict()
        assert router
        assert repr(router) == '<watson.routing.routers.Dict routes:0>'

    def test_instantiate_with_routes(self):
        router = routers.Dict({
            'home': {
                'path': '/'
            }
        })
        assert len(router) == 1

    def test_add_child_routes(self):
        router = routers.Dict({
            'home': {
                'path': '/',
                'children': {
                    'about': {
                        'path': 'about'
                    }
                }
            }
        })
        assert len(router) == 2

    def test_add_child_routes_complex(self):
        router = routers.Dict({
            '1st': {
                'path': '/home',
                'children': {
                    '2nd': {
                        'path': '/:test',
                        'requires': {'test': '\w+'},
                        'children': {
                            '3rd': {
                                'path': '/:tada'
                            }
                        }
                    }
                }
            }
        })
        request = sample_request(PATH_INFO='/home/blah')
        assert router.match(request).route.name == '1st/2nd'
        request = sample_request(PATH_INFO='/home/blah/tada')
        route_match = router.match(request)
        assert route_match.route.name == '1st/2nd/3rd'
        assert route_match.route.requires['test'] == '\w+'
        assert len(router) == 3

    def test_match_route(self):
        request = sample_request()
        router = routers.Dict({
            'home': {
                'path': '/'
            }
        })
        assert next(router.matches(request))
        assert router.match(request)
        assert not router.match(sample_request(PATH_INFO='/test'))

    def test_match_priority_similar_path(self):
        router = routers.Dict({
            'page1': {
                'path': '/page[/:id[/:blah]]',
            },
            'page2': {
                'path': '/page[/:id[/:blah[/:something]]]',
                'priority': 2
            }
        })
        request = sample_request(PATH_INFO='/page')
        match = router.match(request)
        assert match.route.name == 'page2'

    def test_no_match_route(self):
        request = sample_request()
        router = routers.Dict({
            'home': {
                'path': '/about'
            }
        })
        with raises(StopIteration):
            next(router.matches(request))

    def test_assemble(self):
        router = routers.Dict({
            'home': {
                'path': '/'
            }
        })
        assert router.assemble('home') == '/'
        with raises(KeyError):
            router.assemble('no_route')


class TestList(object):
    def test_create(self):
        router = routers.List()
        assert router

    def test_instantiate_with_routes(self):
        router = routers.List([
            {'name': 'home', 'path': '/'}
        ])
        assert len(router) == 1

    def test_invalid_route(self):
        with raises(Exception):
            routers.List([
                {'invalid': 'home', 'path': '/'}
            ])

    def test_multiple_priorities(self):
        router = routers.List([
            {'name': 'about', 'path': '/about'},
            {'name': 'home', 'path': '/'},
        ])
        assert len(router) == 2
        assert list(router.routes.items())[0][0] == 'about'

    def test_add_child_routes(self):
        router = routers.List([
            {
                'name': 'home',
                'path': '/',
                'children': [
                    {'name': 'about', 'path': 'about'}
                ]
            }
        ])
        assert len(router) == 2


class TestChoice(object):

    def test_invalid(self):
        router = routers.Choice()
        with raises(NotImplementedError):
            router.add_route('test')
        with raises(NotImplementedError):
            router.add_definition('test')

    def test_create(self):
        router = routers.Choice(routers.Dict())
        assert router
        assert repr(router) == '<watson.routing.routers.Choice routers:1>'
        router2 = routers.Dict()
        router.add_router(router2)
        assert repr(router) == '<watson.routing.routers.Choice routers:2>'

    def test_get_matched_router(self):
        router = routers.Choice(routers.Dict())
        assert router[routers.Dict]
        assert not router['blah']

    def test_match_route(self):
        request = sample_request(PATH_INFO='/list')
        dict_router = routers.Dict({
            'dict': {
                'path': '/dict',
            }
        })
        list_router = routers.List([
            {'name': 'list', 'path': '/list'}
        ])
        router = routers.Choice(dict_router, list_router)
        match = router.match(request)
        assert match.route.name == 'list'
        assert len(router) == 2
        assert not router.match(sample_request(PATH_INFO='/test'))

    def test_assemble(self):
        list_router = routers.List([
            {'name': 'list', 'path': '/list'}
        ])
        router = routers.Choice(list_router)
        assert router.assemble('list') == '/list'
        with raises(KeyError):
            router.assemble('invalid')
        assert router.assemble('list', query_string={'page': 1}) == '/list?page=1'
        assert 'order=desc' in router.assemble('list', query_string={'page': 1, 'order': 'desc'})
