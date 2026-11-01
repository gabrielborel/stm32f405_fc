"""Compara dois relatorios de DRC em JSON (kicad-cli pcb drc --format json). Somente leitura.

Uso: python3 -I tools/drc_compare.py DEPOIS.json ANTES.json
Mostra violacoes novas que nao sao de silk (com severidade) e a contagem por tipo que mudou.
"""
import collections
import json
import sys

novo = json.load(open(sys.argv[1]))
antigo = json.load(open(sys.argv[2]))


def key(v):
    return (v["type"], tuple(sorted(i["description"] for i in v["items"])))


conhecidas = {key(v) for v in antigo["violations"]}
novas = [v for v in novo["violations"] if key(v) not in conhecidas and not v["type"].startswith("silk")]
print("novas violacoes (exceto silk):", len(novas))
for v in novas:
    print(" ", v["severity"], v["type"], "|", " ; ".join(i["description"] for i in v["items"]))
a = collections.Counter(v["type"] for v in antigo["violations"])
b = collections.Counter(v["type"] for v in novo["violations"])
for k in sorted(set(a) | set(b)):
    if a[k] != b[k]:
        print(" ", k, a[k], "->", b[k])
print("total", len(antigo["violations"]), "->", len(novo["violations"]),
      "| nao conectados", len(antigo["unconnected_items"]), "->", len(novo["unconnected_items"]))
