#!/usr/bin/env python3
"""Generate JSON from CSV, for the certificates system."""

import csv
import sys
import json
import hashlib


def fp(nome, email, local, ano, mes, dia):
    """Compute fingerprint."""
    m = ["", "Janeiro", "Fevereiro", "Março", "Abril",
         "Maio", "Junho", "Julho", "Agosto", "Setembro",
         "Outubro", "Novembro", "Dezembro"]
    data = "%s de %s de %s" % (dia, m[int(mes)], ano)

    oldfinger = (['nh', 'santacruz', 'pelotas', 'poa'], '2017')

    if (local in oldfinger[0]) and (ano == oldfinger[1]):
        data = nome + email + local + dia
    else:
        data = nome + email + local + data

    return hashlib.md5(data.encode('utf-8')).hexdigest()


if len(sys.argv) != 3:
    print("""
    usage:
        gera_lista_participantes.py config.json csv_participantes
            config.json:
                horas: número de horas do evento.
                instituicao: nome da instituicao.
                cidade: nome da cidade em que ocorreu o evento.
                organizacao: numero de horas dos organizadores (opcional).
    """)
    sys.exit(1)

with open(sys.argv[1], "r") as f:
    config = json.load(f)
filename = sys.argv[2]
horas = config.get('horas', 5)
instituicao = config['instituicao']
cidade = config['cidade']
horas_organizacao = config.get('horas_organizacao', horas)

ano, mes, dia, local, *_ = filename.split('-')
ano = ano.split('/')[-1]
local = local.split('.')[0]

with open(filename) as csvfile:
    reader = csv.reader(csvfile)
    lista = [{'nome': row[0],
              'email': row[1],
              'fingerprint': fp(row[0], row[1], local, ano, mes, dia),
              'role': row[3] if len(row) > 3 else "participante"}
             for row in reader
             if row[2] != '' and row[1].lower()[:4] != "nome"]
    participantes = {}
    for x in lista:
        p = participantes.get(x['email'], {'nome': x['nome'],
                                           'email': x['email'],
                                           'fingerprint': x['fingerprint'],
                                           'roles': [],
                                           'palestras': []
                                           })
        roles = p['roles']
        if x['role'] in ['organizador', 'participante']:
            if x['role'] not in roles:
                roles.append(x['role'])
        else:
            if 'palestrante' not in roles:
                roles.append('palestrante')
            palestras = p['palestras']
            if x['role'] not in palestras:
                palestras.append(x['role'])
                p['palestras'] = palestras
        p['roles'] = roles
        participantes[x['email']] = p
evento = {"horas": horas, "instituicao": instituicao,
          "horas_organizacao": horas_organizacao,
          "data": "%s-%s-%s" % (ano, mes, dia), "cidade": cidade,
          "codename": local, "participantes": list(participantes.values())}

with open("data/%s-%s-%s-%s.json" % (ano, mes, dia, local), "w") as outfile:
    print(json.dumps(evento, indent=4, sort_keys=True), file=outfile)
