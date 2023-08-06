from gitcd import Gitcd
import pytest
import os
from shutil import rmtree

test_index = {}
test_repo_name = ["Testing 1", "Testing 2", "Testing 3", "Testing 4"]
test_index_path = {
    "Testing 1": os.path.join("A", "A", "Testing 1"),
    "Testing 2": os.path.join("A", "B", "Testing 2"),
    "Testing 3": os.path.join("B","Testing 3"),
    "Testing 4": "Testing 4"
}

path = None
@pytest.fixture(scope="session", autouse=True)
def setup(tmpdir_factory):
    global path
    path = str(tmpdir_factory.mktemp("gitcd"))
    print("tmpdir: %s" % path)
    
class Test_Gitcd():
    git = Gitcd()

    @classmethod
    def setup_class(cls):
        cls.git.set_index_path_file_path(os.path.join(path, "repo_index.json"))
        for key, item in test_index_path.items():
            full_path = os.path.join(path, item)
            os.makedirs(os.path.join(full_path, ".git"))
            test_index[key] = full_path

    def test_read_not_exist(self):
        assert not self.git.read_repo_index()

    def test_generate(self):
        assert self.git.generate_repo_index(path)

    def test_write(self):
        self.git.write_repo_index()

    def test_read(self):
        assert self.git.read_repo_index()
    
    def test_get_index_file_path(self):
        result = self.git.get_index_file_path()
        assert result == os.path.join(path, "repo_index.json")

    def test_get_repo_index(self):
        result = self.git.get_repo_index()
        assert result == test_index

    def test_get_repo_name_list(self):
        result = self.git.get_repo_name_list()

        assert "Testing 1" in test_index.keys()
        assert "Testing 2" in test_index.keys()
        assert "Testing 3" in test_index.keys()
        assert "Testing 4" in test_index.keys()
    
    def test_get_repo_dir(self):
        result = self.git.get_repo_dir("Testing 1")
        assert result == test_index["Testing 1"]
    
    def test_get_repo_dir_none(self):
        result = self.git.get_repo_dir("Testing 5")
        assert result is None
    
    def test_update(self):
        rmtree(test_index["Testing 2"])
        self.git.update_repo_index()
        result = self.git.get_repo_dir("Testing 2")
        assert result is None