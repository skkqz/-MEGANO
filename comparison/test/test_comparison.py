from django.test import TestCase


class TestSession(TestCase):

    def test_comparison_get(self):
        self.client.get('/comparison/disp')
        session = self.client.session
        session['comparison'] = {'type': 'product', 'id': 1}
        self.assertEqual(session['comparison']['type'], 'product')
        self.assertEqual(session['comparison']['id'], 1)

    def test_comparison_add(self):
        session = self.client.session
        session['comparison'] = [{'type': 'product', 'id': 1}]
        data = {'type': 'product', 'id': 1}
        item_exist = next(
            (item for item in session['comparison'] if item['type'] == data['type']
             and item['id'] == data['id']), False)
        self.client.get('/comparison/1/add')
        if not item_exist:
            session['comparison'].append(data)
            session.save()
        self.assertEqual(len(session['comparison']), 1)

    def test_comparison_remove(self):
        session = self.client.session
        session['comparison'] = [{'type': 'product', 'id': 1}, {'type': 'product_1', 'id': 2}]
        data = {'type': 'product', 'id': 1}
        self.client.get('/comparison/1/remove')
        for item in session['comparison']:
            if item['id'] == data['id'] and item['type'] == data['type']:
                item.clear()
                while {} in session['comparison']:
                    session['comparison'].remove({})
                if not session['comparison']:
                    del session['comparison']
        session.save()
        self.assertEqual(len(session['comparison']), 1)
