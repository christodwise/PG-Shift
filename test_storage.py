import unittest
import os
import storage

class TestStorage(unittest.TestCase):

    def setUp(self):
        # Use a separate test DB file
        storage.DB_FILE = 'test_connections.db'
        storage.init_db()

    def tearDown(self):
        if os.path.exists('test_connections.db'):
            os.remove('test_connections.db')

    def test_save_and_get_connection(self):
        success, msg = storage.save_connection('prod', 'localhost', '5432', 'postgres', 'password', 'mydb')
        self.assertTrue(success)
        
        conns = storage.get_connections()
        self.assertEqual(len(conns), 1)
        self.assertEqual(conns[0]['name'], 'prod')
        self.assertEqual(conns[0]['host'], 'localhost')

    def test_delete_connection(self):
        storage.save_connection('prod', 'localhost', '5432', 'postgres', 'password', 'mydb')
        conns = storage.get_connections()
        conn_id = conns[0]['id']
        
        storage.delete_connection(conn_id)
        conns = storage.get_connections()
        self.assertEqual(len(conns), 0)

if __name__ == '__main__':
    unittest.main()
