import nose
import dpath.util

def test_set_new_separator():
    dict = {
        "a": {
            }
        }
    dpath.util.new(dict, ';a;b', 1, separator=";")
    assert(dict['a']['b'] == 1)
    dpath.util.new(dict, ['a', 'b'], 1, separator=";")
    assert(dict['a']['b'] == 1)

def test_set_new_dict():
    dict = {
        "a": {
            }
        }
    dpath.util.new(dict, '/a/b', 1)
    assert(dict['a']['b'] == 1)
    dpath.util.new(dict, ['a', 'b'], 1)
    assert(dict['a']['b'] == 1)

def test_set_new_list():
    dict = {
        "a": [
            ]
        }
    dpath.util.new(dict, '/a/1', 1)
    assert(dict['a'][1] == 1)
    assert(dict['a'][0] == None)
    dpath.util.new(dict, ['a', '1'], 1)
    assert(dict['a'][1] == 1)
    assert(dict['a'][0] == None)

def test_set_new_list_path_with_separator():
    # This test kills many birds with one stone, forgive me
    dict = {
        "a": {}
        }
    dpath.util.new(dict, ['a', 'b/c/d', 0], 1)
    assert(len(dict['a']) == 1)
    assert(len(dict['a']['b/c/d']) == 1)
    assert(dict['a']['b/c/d'][0] == 1)
    
def test_set_new_list_integer_path_with_creator():
    d = {}
    def mycreator(obj, pathcomp, nextpathcomp):
        print(pathcomp)
        print(nextpathcomp)

        target = pathcomp[0]
        if isinstance(obj, list) and (target.isdigit()):
            target = int(target)
            
        if nextpathcomp and nextpathcomp[0].isdigit():
            obj[target] = [None]*(int(nextpathcomp[0])+1)
        else:
            obj[target] = {}
        print(obj)

    dpath.util.new(d, '/a/2', 3, creator=mycreator)
    print(d)
    assert(isinstance(d['a'], list))
    assert(len(d['a']) == 3)
    assert(d['a'][2] == 3)

