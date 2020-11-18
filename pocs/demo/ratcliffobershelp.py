import difflib

sm = difflib.SequenceMatcher(lambda x: x in " \t.!?,", "test", "text")
print(sm.ratio())
res = difflib.SequenceMatcher(lambda x: x in " \t.!?,", "La télécommande n'est pas bonne.","Le télécommande ne marche pas")
print(res.ratio())
res = difflib.SequenceMatcher(lambda x: x in " \t.!?,", "La télécommande n'est pas bonne.","La télécommande n'est pas bonne. xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
print(res.ratio())
print(res.get_opcodes())

#Plagiat simple mais efficace : https://forum.ubuntu-fr.org/viewtopic.php?id=1235071
