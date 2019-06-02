import unittest

from mafs import router


class RouterTests(unittest.TestCase):
    def test_add(self):
        r = router.Router()
        r.add('/foo', 'in foo')
        self.assertEqual(r.lookup('/foo').data, 'in foo')

        # should not be able to override
        with self.assertRaises(router.RoutingError):
            r.add('/foo', 'in foo again')

    def test_lookup(self):
        r = router.Router()
        r.add('/valid/test', 'in valid/test')

        na = r.lookup('/invalid')
        self.assertEqual(na, None)

        folder = r.lookup('/valid')
        self.assertNotEqual(folder, None)
        self.assertEqual(folder.data, None)

        fil = r.lookup('/valid/test')
        self.assertNotEqual(fil, None)
        self.assertEqual(fil.data, 'in valid/test')

    def test_lookup_parameters(self):
        r = router.Router()

        # single parameter
        r.add('/single/:file', 'in single')
        result = r.lookup('/single/foo')
        self.assertEqual(result.parameters.file, 'foo')

        # multi parameter
        r.add('/double/:folder/:file', 'in double')
        result = r.lookup('/double/foo/bar')
        self.assertEqual(result.parameters.folder, 'foo')
        self.assertEqual(result.parameters.file, 'bar')

        # fallback
        r.add('/fallback/foo', 'in foo')
        r.add('/fallback/:file', 'in fallback')
        self.assertEqual(r.lookup('/fallback/foo').data, 'in foo')
        self.assertEqual(r.lookup('/fallback/other').data, 'in fallback')

    def test_lookup_strings(self):
        # normal path
        r = router.Router()
        r.add('/test/here', 'in test/here')
        self.assertEqual(r.lookup('test/here').data, 'in test/here')
        self.assertEqual(r.lookup('/test/here').data, 'in test/here')
        self.assertEqual(r.lookup('/test//here').data, 'in test/here')

        # without / prefix
        r = router.Router()
        r.add('test/here', 'in test/here')
        self.assertEqual(r.lookup('test/here').data, 'in test/here')
        self.assertEqual(r.lookup('/test/here').data, 'in test/here')
        self.assertEqual(r.lookup('/test//here').data, 'in test/here')

        # with duplicates
        r = router.Router()
        r.add('test//here', 'in test/here')
        self.assertEqual(r.lookup('test/here').data, 'in test/here')
        self.assertEqual(r.lookup('/test/here').data, 'in test/here')
        self.assertEqual(r.lookup('/test//here').data, 'in test/here')

    def test_list(self):
        r = router.Router()
        r.add('/foo', 'in foo')
        r.add('/bar', 'in bar')
        r.add('/baz', 'in baz')

        self.assertEqual(r.list('/').data, ['foo', 'bar', 'baz'])


if __name__ == "__main__":
    unittest.main()
