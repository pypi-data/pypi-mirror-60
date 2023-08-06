import context

from zincbase import KB

kb = KB()
kb.seed(555)

kb.store('person(tom)')
kb.store('person(shamala)')
kb.store('knows(tom, shamala)')
assert kb.neighbors('tom') == [('shamala', [{'pred': 'knows'}])]

kb.attr('tom', { 'grains': 0 })

tom = kb.node('tom')
assert tom.grains == 0
assert tom.i_dont_exist is None
assert tom['i_dont_exist'] is None

kb.attr('shamala', { 'grains': 4 })
shamala = kb.node('shamala')
assert shamala.grains == 4
shamala.grains += 1
assert shamala.grains == 5
assert shamala['grains'] == 5
shamala['grains'] += 1
assert shamala['grains'] == 6

kb.store('person(jeraca)')
kb.attr('jeraca', { 'grains': 3 })

zero_grains = list(kb.filter(lambda x: x['grains'] == 0))
assert len(zero_grains) == 1
assert zero_grains[0] == 'tom'
assert zero_grains[0] != 'shamala'

zero_anything = list(kb.filter(lambda x: x['anything'] == 0))
assert len(zero_anything) == 0

more_grains = kb.filter(lambda x: x['grains'] >= 3)
assert next(more_grains) in ['shamala', 'jeraca']
assert next(more_grains) in ['shamala', 'jeraca']

more_grains = kb.filter(lambda x: x['grains'] >= 3, candidate_nodes=['shamala'])
as_list = list(more_grains)
assert as_list == ['shamala']

more_grains = kb.filter(lambda x: x['grains'] >= 3, candidate_nodes=[])
as_list = list(more_grains)
assert as_list == []

some_or_no_grains = kb.filter(lambda x: x['grains'] >= -1, candidate_nodes=['tom', 'shamala'])
as_list = list(some_or_no_grains)
assert len(as_list) == 2
assert as_list[0] in ['tom', 'shamala']
assert as_list[1] in ['tom', 'shamala']
assert as_list[0] != as_list[1]

nodes = kb.filter(lambda x: True)
as_list = list(nodes)
assert len(as_list) == 3
jeraca = kb.node('jeraca')
assert len(jeraca.neighbors) == 0
shamala = kb.node('shamala')
assert len(shamala.neighbors) == 0
tom = kb.node('tom')
assert len(tom.neighbors) == 1
assert tom.neighbors[0][0] == 'shamala'
assert len(tom.neighbors[0][1]) == 1
assert tom.neighbors[0][1][0]['pred'] == 'knows'

print('All attribute tests passed.')