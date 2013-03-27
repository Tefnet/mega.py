import os
import tempfile
import random
import string
import hashlib
import unittest
from mega import Mega

def randomstring(length=30):
    return ''.join(random.choice(string.ascii_letters + string.digits) for n in xrange(length))

class TestAPI(unittest.TestCase):
    longMessage = True
    keys_get_user = set([u'c', u'k', u'ts', u'n', u's', u'u'])
    keys_dir = set([u'a', u'h', u'k', u'ts', u'p', u'u', u't'])
    keys_file = set([u'a', u'h', u'k', u'ts', 'iv', u'p', u's', 'meta_mac', u'u', u't'])
    test_filesize = 256*1024 # 256KB
    
    @classmethod
    def login(cls):
        mega = Mega()
        cls.m = mega.login()

    @classmethod
    def gen_test_file(cls):
        test_fd, cls.test_filepath = tempfile.mkstemp()
        test_file = os.fdopen(test_fd, 'w')
        cls.test_filename = os.path.basename(cls.test_filepath)
        remaining = cls.test_filesize
        filehash = hashlib.sha256()
        while remaining > 0:
            n = min(remaining, 2**18)
            data = os.urandom(n)
            filehash.update(data)
            test_file.write(data)
            remaining = remaining - n

        test_file.close()
        cls.test_filehash = filehash.digest()
        assert os.path.getsize(cls.test_filepath) == cls.test_filesize
        
    @classmethod
    def setUpClass(cls):
        cls.login()
        cls.tmp_prefix = randomstring(30)
        tmpdir = cls.m.create_folder('%s_tmpdir' % cls.tmp_prefix)
        cls.tmpdir_node_id = tmpdir['f'][0]['h']
        cls.gen_test_file()

    @classmethod
    def tearDownClass(cls):
        if cls.tmpdir_node_id:
            cls.m.destroy(cls.tmpdir_node_id)
        os.unlink(cls.test_filepath)
    
    def test_get_user(self):
        '''get user details'''
        rval = self.m.get_user()
        self.assertIsInstance(rval, dict)
        self.assertSetEqual(set(rval.keys()), self.keys_get_user, "Result keys don't match")

    def test_get_quota(self):
        '''get storage quota'''
        rval = self.m.get_quota()
        self.assertIsInstance(rval, long)

    def test_get_files(self):
        rval = self.m.get_files()
        self.assertIsInstance(rval, dict)
        for node in rval.values():
            if node['t']>0:
                self.assertSetEqual(set(node.keys()), self.keys_dir, 'Wrong node keys for directory "%s"' % (node['a']['n'],))
            else:
                self.assertSetEqual(set(node.keys()), self.keys_file, 'Wrong node keys for file "%s"' % (node['a']['n'],))

    def test_upload(self):
        '''upload file'''
        rval = self.m.upload(self.test_filepath, self.tmpdir_node_id)
        fnode = rval['f'][0]
        # Verify upload result
        self.assertEqual(fnode['s'], self.test_filesize)
        self.assertEqual(fnode['p'], self.tmpdir_node_id)

        rval = self.m.find(self.test_filename)
        fnode = rval[1]
        # Verify find result
        self.assertEqual(fnode['s'], self.test_filesize)
        self.assertEqual(fnode['p'], self.tmpdir_node_id)
        self.assertEqual(fnode['a']['n'], self.test_filename)

    def test_upload_dest_filename(self):
        '''upload file (change destination filename)'''
        tmp_filename = randomstring(30)
        rval = self.m.upload(self.test_filepath, self.tmpdir_node_id, dest_filename=tmp_filename)
        fnode = rval['f'][0]
        # Verify upload result
        self.assertEqual(fnode['s'], self.test_filesize)
        self.assertEqual(fnode['p'], self.tmpdir_node_id)

        rval = self.m.find(tmp_filename)
        fnode = rval[1]
        # Verify find result
        self.assertEqual(fnode['s'], self.test_filesize)
        self.assertEqual(fnode['p'], self.tmpdir_node_id)
        self.assertEqual(fnode['a']['n'], tmp_filename)


    def test_download(self):
        '''download file'''
        tmp_filename = randomstring(30)
        tmp_path = os.path.join(tempfile.gettempdir(), tmp_filename)
        self.m.upload(self.test_filepath, self.tmpdir_node_id, dest_filename=tmp_filename)
        rfile = self.m.find(tmp_filename)

        # download file by file object
        self.m.download(rfile, tempfile.gettempdir())
        self.assertEqual(os.path.getsize(tmp_path), rfile[1]['s'])
        os.unlink(tmp_path)

        # download file by file url
        dlink = self.m.get_link(rfile)
        self.m.download_url(dlink, tempfile.gettempdir())
        self.assertEqual(os.path.getsize(tmp_path), rfile[1]['s'])
        os.unlink(tmp_path)

if os.environ.has_key('MEGA_EMAIL'):
    class TestAPIAuthorized(TestAPI):
        keys_get_user = set([u'c', u'k', u'ts', u's', u'u', u'pubk', u'privk', u'name', u'email'])

        @classmethod
        def login(cls):
            mega = Mega()
            cls.m = mega.login(os.environ.get('MEGA_EMAIL'), os.environ.get('MEGA_PASSWORD'))

if __name__ == '__main__':
    unittest.main(verbosity=2)
