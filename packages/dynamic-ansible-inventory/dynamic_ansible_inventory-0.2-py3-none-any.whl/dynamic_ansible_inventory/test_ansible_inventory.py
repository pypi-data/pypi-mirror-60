import os
import unittest
import ansible_inventory


class Test_ansible_inventory(unittest.TestCase):
    def test_add_section(self):
        ai = ansible_inventory.ansible_inventory()
        ai.add_section("test")
        self.assertDictEqual(ai._sections, {'test': {}})

    def test_duplicate_add_section(self):
        with self.assertRaises(ansible_inventory.DuplicateSectionError):
            self.duplicate_add_section()

    def duplicate_add_section(self):
        ai = ansible_inventory.ansible_inventory()
        ai.add_section("test")
        ai.add_section("test")

    def test_set(self):
        ai = ansible_inventory.ansible_inventory()
        ai.add_section("test")
        ai.set("test", "192.168.1.1", "ansible_ssh_user=root ansible_ssh_pass=hoge")
        self.assertDictEqual(ai._sections, {'test': {'192.168.1.1': 'ansible_ssh_user=root ansible_ssh_pass=hoge'}})

    def test_duplicate_set(self):
        ai = ansible_inventory.ansible_inventory()
        ai.add_section("test")
        ai.set("test", "192.168.1.1", "ansible_ssh_user=root ansible_ssh_pass=hoge")
        ai.set("test", "192.168.1.1", "ansible_ssh_user=root ansible_ssh_pass=huga")
        self.assertDictEqual(ai._sections, {'test': {'192.168.1.1': 'ansible_ssh_user=root ansible_ssh_pass=huga'}})

    def test_nosection_set(self):
        with self.assertRaises(ansible_inventory.NoSectionError):
            self.nosection_set()

    def nosection_set(self):
        ai = ansible_inventory.ansible_inventory()
        ai.set("test", "key", "value")

    def test_write(self):
        wont = ["[test]\n", "192.168.1.1 ansible_ssh_user=root ansible_ssh_pass=hoge\n", "192.168.1.2 ansible_ssh_user=root ansible_ssh_pass=hoge\n"]
        test_path = "/tmp/test"

        ai = ansible_inventory.ansible_inventory()
        ai.add_section("test")
        ai.set("test", "192.168.1.1", "ansible_ssh_user=root ansible_ssh_pass=hoge")
        ai.set("test", "192.168.1.2", "ansible_ssh_user=root ansible_ssh_pass=hoge")
        with open(test_path, "w") as fp:
            ai.write(fp)
        self.assertTrue(os.path.exists("/tmp/test"))
        with open(test_path, "r") as fp:
            i = 0
            for line in fp.readlines():
                self.assertEqual(line, wont[i])
                i = i + 1
        os.remove(test_path)


if __name__ == '__main__':
    unittest.main()
