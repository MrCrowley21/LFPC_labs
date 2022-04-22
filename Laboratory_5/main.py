from LL1 import LL1

ll1 = LL1('Variant_12.txt')
ll1.parse('abgdcf')  # accepted (word from condition)
# ll1.parse('abecf')  # accepted
# ll1.parse('abf')  # not accepted
# ll1.parse('efefebeg')  # for 'test.txt'
# ll1.parse('acaba')  # for 'test_2.txt'
