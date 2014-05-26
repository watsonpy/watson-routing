# -*- coding: utf-8 -*-
from watson.routing import routers
from pytest import raises
from tests.watson.routing.support import sample_request


class TestDictRouter(object):
    def test_create(self):
        router = routers.DictRouter()
        assert router
        assert repr(router) == '<watson.routing.routers.DictRouter routes:0>'

    def test_instantiate_with_routes(self):
        router = routers.DictRouter({
            'home': {
                'path': '/'
            }
        })
        assert len(router) == 1

    def test_add_child_routes(self):
        router = routers.DictRouter({
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

    def test_match_route(self):
        request = sample_request()
        router = routers.DictRouter({
            'home': {
                'path': '/'
            }
        })
        assert next(router.matches(request))
        assert router.match(request)
        assert not router.match(sample_request(PATH_INFO='/test'))

    def test_match_priority_similar_path(self):
        router = routers.DictRouter({
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
        router = routers.DictRouter({
            'home': {
                'path': '/about'
            }
        })
        with raises(StopIteration):
            next(router.matches(request))

    def test_assemble(self):
        router = routers.DictRouter({
            'home': {
                'path': '/'
            }
        })
        assert router.assemble('home') == '/'
        with raises(KeyError):
            router.assemble('no_route')


class TestListRouter(object):
    def test_create(self):
        router = routers.ListRouter()
        assert router

    def test_instantiate_with_routes(self):
        router = routers.ListRouter([
            {'name': 'home', 'path': '/'}
        ])
        assert len(router) == 1

    def test_invalid_route(self):
        with raises(Exception):
            routers.ListRouter([
                {'invalid': 'home', 'path': '/'}
            ])

    def test_multiple_priorities(self):
        router = routers.ListRouter([
            {'name': 'about', 'path': '/about'},
            {'name': 'home', 'path': '/'},
        ])
        assert len(router) == 2
        assert list(router.routes.items())[0][0] == 'about'

    def test_add_child_routes(self):
        router = routers.ListRouter([
            {
                'name': 'home',
                'path': '/',
                'children': [
                    {'name': 'about', 'path': 'about'}
                ]
            }
        ])
        assert len(router) == 2


class TestChoiceRouter(object):

    def test_invalid(self):
        router = routers.ChoiceRouter()
        with raises(NotImplementedError):
            router.add_route('test')
        with raises(NotImplementedError):
            router.add_definition('test')

    def test_create(self):
        router = routers.ChoiceRouter(routers.DictRouter())
        assert router
        assert repr(router) == '<watson.routing.routers.ChoiceRouter routers:1>'
        router2 = routers.DictRouter()
        router.add_router(router2)
        assert repr(router) == '<watson.routing.routers.ChoiceRouter routers:2>'

    def test_get_matched_router(self):
        router = routers.ChoiceRouter(routers.DictRouter())
        assert router[routers.DictRouter]
        assert not router['blah']

    def test_match_route(self):
        request = sample_request(PATH_INFO='/list')
        dict_router = routers.DictRouter({
            'dict': {
                'path': '/dict',
            }
        })
        list_router = routers.ListRouter([
            {'name': 'list', 'path': '/list'}
        ])
        router = routers.ChoiceRouter(dict_router, list_router)
        match = router.match(request)
        assert match.route.name == 'list'
        assert len(router) == 2
        assert not router.match(sample_request(PATH_INFO='/test'))

    def test_assemble(self):
        list_router = routers.ListRouter([
            {'name': 'list', 'path': '/list'}
        ])
        router = routers.ChoiceRouter(list_router)
        assert router.assemble('list') == '/list'
        with raises(KeyError):
            router.assemble('invalid')
