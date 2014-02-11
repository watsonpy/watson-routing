# -*- coding: utf-8 -*-
from pytest import raises
from tests.watson.routing import support
from watson.http import REQUEST_METHODS
from watson.routing import routes


class TestBaseRoute(object):
    def test_properties(self):
        class MyRoute(routes.BaseRoute):
            pass

        with raises(NotImplementedError):
            MyRoute.builder(True)

        route = MyRoute(name='home', path='/', requires={'format': 'xml'})
        assert route.accepts == REQUEST_METHODS
        assert not route.defaults
        assert not route.options
        assert route.priority == 1
        assert route.name == 'home'
        assert route.path == '/'
        assert route.requires['format']
        with raises(NotImplementedError):
            route.assemble()


class TestLiteralRoute(object):
    def test_create(self):
        route = routes.LiteralRoute(name='home', path='/', accepts=('GET',))
        assert route
        assert route.accepts == ('GET',)
        assert repr(route) == '<watson.routing.routes.LiteralRoute name:home path:/>'

    def test_match(self):
        route = routes.LiteralRoute(name='home', path='/')
        assert route.match(support.sample_request())

    def test_no_accept_match(self):
        route = routes.LiteralRoute(name='home', path='/', accepts=('POST',))
        assert not route.match(support.sample_request())

    def test_accept_match(self):
        route = routes.LiteralRoute(name='home', path='/', accepts=('POST',))
        assert route.match(support.sample_request(REQUEST_METHOD='POST'))

    def test_no_subdomain_match(self):
        route = routes.LiteralRoute(
            name='home', path='/', requires={'subdomain': 'test'})
        route2 = routes.LiteralRoute(
            name='home', path='/', requires={'subdomain': ('test',)})
        request = support.sample_request()
        assert not route.match(request)
        assert not route2.match(request)

    def test_subdomain_match(self):
        request = support.sample_request(SERVER_NAME='clients2.test.com',
                                         HTTP_HOST='clients2.test.com')
        route = routes.LiteralRoute(
            name='home', path='/', requires={'subdomain': 'clients2'})
        assert route.match(request)

    def test_format_match(self):
        route = routes.LiteralRoute(
            name='home', path='/', requires={'format': 'xml'})
        assert route.match(support.sample_request(HTTP_ACCEPT='text/xml'))

    def test_no_format_match(self):
        route = routes.LiteralRoute(
            name='home', path='/', requires={'format': 'xml'})
        assert not route.match(support.sample_request(HTTP_ACCEPT='text/json'))

    def test_get_match(self):
        request = support.sample_request(QUERY_STRING='test=blah')
        route = routes.LiteralRoute(
            name='home', path='/', requires={'test': '^blah'})
        assert route.match(request)

    def test_no_get_match(self):
        request = support.sample_request(QUERY_STRING='test=test')
        route = routes.LiteralRoute(
            name='home', path='/', requires={'test': 'blah'})
        match = route.match(request)
        assert not match

    def test_assemble(self):
        route = routes.LiteralRoute(name='home', path='/')
        assert route.assemble() == '/'
        assert route.assemble(prefix='http://127.0.0.1') == 'http://127.0.0.1/'


class TestSegmentRoute(object):
    def test_create(self):
        route = routes.SegmentRoute(name='home', path='/')
        assert route
        assert repr(route) == '<watson.routing.routes.SegmentRoute name:home path:/ match:\/$>'

    def test_create_regex_instead_of_path(self):
        with raises(TypeError):
            routes.SegmentRoute(name='home')
        route = routes.SegmentRoute(name='home', regex='/test')
        assert route
        assert repr(route) == '<watson.routing.routes.SegmentRoute name:home match:\/test$>'

    def test_builder(self):
        assert routes.SegmentRoute.builder(name='test', path='/:test')

    def test_match(self):
        route = routes.SegmentRoute(name='home', path='/:test')
        assert route.match(support.sample_request(PATH_INFO='/blah'))

    def test_no_match(self):
        route = routes.SegmentRoute(name='home', path='/:test', accepts=('GET',))
        assert not route.match(support.sample_request(PATH_INFO='/'))
        assert not route.match(
            support.sample_request(PATH_INFO='/test', REQUEST_METHOD='POST'))

    def test_optional_match(self):
        optional = routes.SegmentRoute(name='home', path='/about[/:company]')
        optional_nested = routes.SegmentRoute(name='home', path='/about[/:company[/:test]]')
        optional_required = routes.SegmentRoute(name='home', path='/about[/:company/:test]')
        request = support.sample_request(PATH_INFO='/about/test')
        request2 = support.sample_request(PATH_INFO='/about/test')
        request3 = support.sample_request(PATH_INFO='/about/test/blah')
        assert optional.match(request)
        assert len(optional.segments) == 2
        assert optional_nested.match(request2)
        assert optional_required.match(request3)
        assert not optional_required.match(request2)

    def test_optional_params(self):
        route = routes.SegmentRoute(name='home', path='/about[/:company]', defaults={'company': 'test'})
        request = support.sample_request(PATH_INFO='/about')
        assert route.match(request).params['company'] == 'test'

    def test_segment_bracket_mismatch(self):
        with raises(ValueError):
            routes.SegmentRoute(name='mismatch', path='/search:keyword]')

    def test_assemble(self):
        route = routes.SegmentRoute(name='home', path='/:test')
        optional = routes.SegmentRoute(name='home', path='/about[/:test]')
        optional_nested = routes.SegmentRoute(name='home', path='/about[/:company[/:test]]')
        assert route.assemble(test='blah') == '/blah'
        assert route.assemble(
            prefix='http://127.0.0.1', test='blah') == 'http://127.0.0.1/blah'
        assert optional.assemble(test='blah') == '/about/blah'
        assert optional_nested.assemble(company='testing') == '/about/testing'
        assert optional_nested.assemble(company='testing', test='blah') == '/about/testing/blah'
        with raises(KeyError):
            route.assemble()
