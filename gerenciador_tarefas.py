#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime, timedelta
import sys

# ---------------------------
# Declaração de variáveis globais
# ---------------------------
TAREFAS_FILE = "tarefas.json"
TAREFAS_ARQUIVADAS_FILE = "tarefas_arquivadas.json"

# listas/estruturas globais
tarefas = []         # lista principal de tarefas (cada tarefa é um dict)
tarefas_arquivadas = []  # histórico acumulado no arquivo de arquivamento
next_id = 1          # controle global do ID (será carregado/ajustado do arquivo)

# Constantes do sistema
PRIORIDADES = ["Urgente", "alta", "média", "baixa"]  # ordem de busca para urgência (máxima -> mínima)
STATUS_VALIDOS = ["Pendente", "Fazendo", "Concluída", "Arquivado", "Excluída"]
ORIGENS_VALIDAS = ["E-mail", "Telefone", "Chamado do Sistema"]

# ---------------------------
# Funções de persistência e utilitários
# ---------------------------

def print_debug(msg):
    """Imprime mensagem de debug padronizada."""
    print(f"[DEBUG] {msg}")

def ensure_files_exist():
    """
    Garante que os arquivos tarefas.json e tarefas_arquivadas.json existam.
    Se não existirem, cria com estrutura inicial válida (lista vazia).
    """
    print("Executando a função ensure_files_exist")
    global TAREFAS_FILE, TAREFAS_ARQUIVADAS_FILE
    if not os.path.exists(TAREFAS_FILE):
        with open(TAREFAS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        print_debug(f"Arquivo criado: {TAREFAS_FILE}")
    if not os.path.exists(TAREFAS_ARQUIVADAS_FILE):
        with open(TAREFAS_ARQUIVADAS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        print_debug(f"Arquivo criado: {TAREFAS_ARQUIVADAS_FILE}")

def carregar_dados():
    """
    Carrega os dados dos arquivos JSON para as variáveis globais.
    Converte datas em strings ISO para objetos datetime em memória.
    Ajusta next_id com base no maior ID encontrado.
    """
    print("Executando a função carregar_dados")
    global tarefas, tarefas_arquivadas, next_id

    ensure_files_exist()

    # Carregar tarefas principais
    try:
        with open(TAREFAS_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
            tarefas = []
            max_id_local = 0
            for item in raw:
                # converter datas ISO para datetime (se existirem)
                tarefa = item.copy()
                if tarefa.get("creation_date"):
                    tarefa["creation_date"] = datetime.fromisoformat(tarefa["creation_date"])
                if tarefa.get("completion_date"):
                    tarefa["completion_date"] = datetime.fromisoformat(tarefa["completion_date"])
                tarefas.append(tarefa)
                if isinstance(tarefa.get("id"), int) and tarefa["id"] > max_id_local:
                    max_id_local = tarefa["id"]
            if max_id_local >= next_id:
                next_id = max_id_local + 1
            print_debug(f"{len(tarefas)} tarefas carregadas. next_id={next_id}")
    except Exception as e:
        print("Erro ao carregar tarefas:", e)
        tarefas = []

    # Carregar arquivo de arquivadas (histórico)
    try:
        with open(TAREFAS_ARQUIVADAS_FILE, "r", encoding="utf-8") as f:
            raw2 = json.load(f)
            tarefas_arquivadas = raw2  # aqui mantemos como dados serializáveis (strings ISO)
            print_debug(f"{len(tarefas_arquivadas)} registros em tarefas_arquivadas carregados.")
    except Exception as e:
        print("Erro ao carregar tarefas_arquivadas:", e)
        tarefas_arquivadas = []

def salvar_dados():
    """
    Persiste as variáveis globais em arquivos JSON.
    Converte datetime em ISO strings antes de gravar.
    """
    print("Executando a função salvar_dados")
    global tarefas, tarefas_arquivadas

    try:
        serializavel = []
        for t in tarefas:
            t_copy = t.copy()
            if isinstance(t_copy.get("creation_date"), datetime):
                t_copy["creation_date"] = t_copy["creation_date"].isoformat()
            if isinstance(t_copy.get("completion_date"), datetime):
                t_copy["completion_date"] = t_copy["completion_date"].isoformat()
            serializavel.append(t_copy)
        with open(TAREFAS_FILE, "w", encoding="utf-8") as f:
            json.dump(serializavel, f, ensure_ascii=False, indent=4)
        print_debug(f"Tarefas salvas em {TAREFAS_FILE}")
    except Exception as e:
        print("Erro ao salvar tarefas:", e)

    try:
        # tarefas_arquivadas já contém dados serializáveis (ISO strings), então apenas salvar
        with open(TAREFAS_ARQUIVADAS_FILE, "w", encoding="utf-8") as f:
            json.dump(tarefas_arquivadas, f, ensure_ascii=False, indent=4)
        print_debug(f"Tarefas arquivadas salvas em {TAREFAS_ARQUIVADAS_FILE}")
    except Exception as e:
        print("Erro ao salvar tarefas_arquivadas:", e)

def obter_tarefa_por_id(tid):
    """
    Retorna a tarefa (dicionário) com o id informado ou None se não existir.
    Parâmetros:
        tid (int): ID da tarefa
    Retorno:
        dict ou None
    """
    print("Executando a função obter_tarefa_por_id")
    for t in tarefas:
        if t.get("id") == tid:
            return t
    return None

def validar_prioridade(p):
    """
    Valida se a prioridade informada está entre as prioridades do sistema.
    Retorna a prioridade normalizada (string) se válida; None caso contrário.
    """
    print("Executando a função validar_prioridade")
    if not isinstance(p, str):
        return None
    for pr in PRIORIDADES:
        if p.strip().lower() == pr.lower():
            return pr
    return None

def validar_origem(o):
    """
    Valida a origem informada.
    """
    print("Executando a função validar_origem")
    if not isinstance(o, str):
        return None
    for og in ORIGENS_VALIDAS:
        if o.strip().lower() == og.lower():
            return og
    return None

def validar_status(s):
    """
    Valida o status informado.
    """
    print("Executando a função validar_status")
    if not isinstance(s, str):
        return None
    for st in STATUS_VALIDOS:
        if s.strip().lower() == st.lower():
            return st
    return None

# ---------------------------
# Funções principais do sistema (cada uma com docstring e print no início)
# ---------------------------

def criar_tarefa():
    """
    Cria uma nova tarefa solicitando informações ao usuário,
    valida os dados e adiciona a tarefa à lista global de tarefas.
    Parâmetros: nenhum
    Retorno: nenhum
    """
    print("Executando a função criar_tarefa")
    global tarefas, next_id

    # Título obrigatório
    while True:
        titulo = input("Título (obrigatório): ").strip()
        if titulo:
            break
        print("Título não pode ser vazio. Tente novamente.")

    descricao = input("Descrição (opcional): ").strip()

    # Mostrar opções de prioridade
    print("Opções de Prioridade:", ", ".join(PRIORIDADES))
    while True:
        pri_input = input("Prioridade (obrigatório): ").strip()
        pri = validar_prioridade(pri_input)
        if pri:
            break
        print("Prioridade inválida. Use uma das opções:", ", ".join(PRIORIDADES))

    # Status começa como Pendente
    status = "Pendente"

    # Origem obrigatória
    print("Opções de Origem:", ", ".join(ORIGENS_VALIDAS))
    while True:
        origem_input = input("Origem da Tarefa (obrigatório): ").strip()
        origem = validar_origem(origem_input)
        if origem:
            break
        print("Origem inválida. Use uma das opções:", ", ".join(ORIGENS_VALIDAS))

    # Data de criação = agora
    creation_date = datetime.now()

    # Construir tarefa
    tarefa = {
        "id": next_id,
        "titulo": titulo,
        "descricao": descricao,
        "prioridade": pri,
        "status": status,
        "origem": origem,
        "creation_date": creation_date,
        "completion_date": None  # será datetime quando concluída
    }

    tarefas.append(tarefa)
    print(f"Tarefa criada com ID {next_id}.")
    next_id += 1

def verificar_urgencia_e_pegar():
    """
    Verifica se há tarefas com prioridade máxima (Urgente) e seleciona a primeira encontrada.
    Se não houver, busca na próxima prioridade. Atualiza o status da tarefa selecionada para 'Fazendo'.
    Garante que somente uma tarefa esteja em 'Fazendo' por vez: se houver outra, ela volta para 'Pendente'.
    """
    print("Executando a função verificar_urgencia_e_pegar")
    global tarefas

    # primeiro, rodar limpeza de arquivamento automático (opcionalmente)
    arquivar_tarefas_concluidas_antigas()

    # localizar a primeira tarefa 'Pendente' seguindo a ordem de PRIORIDADES
    selecionada = None
    for pr in PRIORIDADES:
        for t in tarefas:
            if (t.get("prioridade") == pr) and (t.get("status") == "Pendente"):
                selecionada = t
                break
        if selecionada:
            break

    if not selecionada:
        print("Não há tarefas pendentes para pegar.")
        return

    # conferir se já existe alguma em Fazendo
    outra_fazendo = None
    for t in tarefas:
        if t.get("status") == "Fazendo":
            outra_fazendo = t
            break

    if outra_fazendo:
        # policy: voltar a anterior para Pendente (poderíamos também impedir; aqui optamos por trocar)
        outra_fazendo["status"] = "Pendente"
        print_debug(f"Tarefa ID {outra_fazendo['id']} que estava em 'Fazendo' retornou para 'Pendente'.")

    selecionada["status"] = "Fazendo"
    print(f"Tarefa selecionada para execução: ID {selecionada['id']} - {selecionada['titulo']} (Prioridade: {selecionada['prioridade']})")

def atualizar_prioridade():
    """
    Permite alterar a prioridade de uma tarefa informando seu ID.
    Valida se a nova prioridade pertence às prioridades do sistema.
    """
    print("Executando a função atualizar_prioridade")
    global tarefas
    try:
        tid = int(input("Informe o ID da tarefa para atualizar prioridade: ").strip())
    except Exception:
        print("ID inválido. Operação cancelada.")
        return

    tarefa = obter_tarefa_por_id(tid)
    if not tarefa:
        print(f"Tarefa com ID {tid} não encontrada.")
        return

    print(f"Tarefa encontrada: ID {tarefa['id']} - {tarefa['titulo']} (Prioridade atual: {tarefa['prioridade']})")
    print("Opções de Prioridade:", ", ".join(PRIORIDADES))
    novo = input("Nova prioridade: ").strip()
    pri_normalizada = validar_prioridade(novo)
    if not pri_normalizada:
        print("Prioridade inválida. Operação cancelada.")
        return

    tarefa["prioridade"] = pri_normalizada
    print(f"Prioridade da tarefa ID {tid} atualizada para {pri_normalizada}.")

def concluir_tarefa():
    """
    Marca uma tarefa como concluída.
    Adiciona data/hora de conclusão (datetime) somente para tarefas finalizadas.
    Atualiza status para 'Concluída'.
    """
    print("Executando a função concluir_tarefa")
    global tarefas
    try:
        tid = int(input("Informe o ID da tarefa a concluir: ").strip())
    except Exception:
        print("ID inválido.")
        return

    tarefa = obter_tarefa_por_id(tid)
    if not tarefa:
        print("Tarefa não encontrada.")
        return

    if tarefa.get("status") == "Concluída":
        print("Tarefa já está marcada como Concluída.")
        return

    # Definir data de conclusão
    tarefa["completion_date"] = datetime.now()
    tarefa["status"] = "Concluída"
    print(f"Tarefa ID {tid} marcada como Concluída em {tarefa['completion_date'].isoformat()}.")

def arquivar_tarefas_concluidas_antigas():
    """
    Atualiza status para 'Arquivado' para tarefas concluídas há mais de 7 dias.
    Registra essas tarefas no arquivo tarefas_arquivadas.json (variável tarefas_arquivadas),
    acumulando o histórico. Não remove da lista principal (apenas altera o status).
    """
    print("Executando a função arquivar_tarefas_concluidas_antigas")
    global tarefas, tarefas_arquivadas

    # carregar arquivo de arquivadas atual (para evitar duplicatas)
    try:
        with open(TAREFAS_ARQUIVADAS_FILE, "r", encoding="utf-8") as f:
            historico_raw = json.load(f)
    except Exception:
        historico_raw = []

    ids_arquivados_existentes = {item.get("id") for item in historico_raw}

    hoje = datetime.now()
    novas_arquivadas = []
    for t in tarefas:
        if t.get("status") == "Concluída" and isinstance(t.get("completion_date"), datetime):
            delta = hoje - t["completion_date"]
            if delta > timedelta(days=7):
                # marcar como Arquivado
                t["status"] = "Arquivado"
                # preparar registro serializável para arquivo de arquivamento
                registro = t.copy()
                if isinstance(registro.get("creation_date"), datetime):
                    registro["creation_date"] = registro["creation_date"].isoformat()
                if isinstance(registro.get("completion_date"), datetime):
                    registro["completion_date"] = registro["completion_date"].isoformat()
                if registro.get("id") not in ids_arquivados_existentes:
                    novas_arquivadas.append(registro)
                    ids_arquivados_existentes.add(registro.get("id"))

    if novas_arquivadas:
        # atualizar arquivo de arquivadas acumulando histórico
        historico_raw.extend(novas_arquivadas)
        try:
            with open(TAREFAS_ARQUIVADAS_FILE, "w", encoding="utf-8") as f:
                json.dump(historico_raw, f, ensure_ascii=False, indent=4)
            tarefas_arquivadas = historico_raw
            print(f"{len(novas_arquivadas)} tarefa(s) arquivada(s) por tempo (>7 dias) e registrada(s) em {TAREFAS_ARQUIVADAS_FILE}.")
        except Exception as e:
            print("Erro ao atualizar arquivo de arquivamento:", e)

def exclusao_logica():
    """
    Realiza exclusão lógica: marca uma tarefa com status 'Excluída', sem removê-la da lista.
    """
    print("Executando a função exclusao_logica")
    global tarefas
    try:
        tid = int(input("Informe o ID da tarefa a excluir (exclusão lógica): ").strip())
    except Exception:
        print("ID inválido.")
        return

    tarefa = obter_tarefa_por_id(tid)
    if not tarefa:
        print("Tarefa não encontrada.")
        return

    tarefa["status"] = "Excluída"
    print(f"Tarefa ID {tid} marcada como 'Excluída' (exclusão lógica).")

def relatorio_completo():
    """
    Exibe todas as informações das tarefas na tela.
    Para tarefas concluídas calcula e exibe o tempo de execução (duração entre criação e conclusão).
    """
    print("Executando a função relatorio_completo")
    if not tarefas:
        print("Nenhuma tarefa cadastrada.")
        return

    for t in tarefas:
        print("-" * 60)
        print(f"ID: {t.get('id')}")
        print(f"Título: {t.get('titulo')}")
        print(f"Descrição: {t.get('descricao')}")
        print(f"Prioridade: {t.get('prioridade')}")
        print(f"Status: {t.get('status')}")
        print(f"Origem: {t.get('origem')}")
        cd = t.get("creation_date")
        if isinstance(cd, datetime):
            print(f"Data de Criação: {cd.isoformat()}")
        else:
            print(f"Data de Criação: {cd}")
        comp = t.get("completion_date")
        if comp:
            # comp pode ser datetime
            if isinstance(comp, datetime):
                print(f"Data de Conclusão: {comp.isoformat()}")
                # calcular tempo de execução
                if isinstance(cd, datetime):
                    dur = comp - cd
                    dias = dur.days
                    horas = dur.seconds // 3600
                    minutos = (dur.seconds % 3600) // 60
                    print(f"Tempo de execução: {dias} dia(s), {horas} hora(s), {minutos} minuto(s)")
                else:
                    print("Tempo de execução: impossível calcular (data de criação inválida).")
            else:
                print(f"Data de Conclusão: {comp}")
        else:
            print("Data de Conclusão: ---")
    print("-" * 60)

def relatorio_arquivados():
    """
    Exibe a lista de tarefas arquivadas (status 'Arquivado').
    Tarefas com status 'Excluída' não devem ser mostradas neste relatório.
    """
    print("Executando a função relatorio_arquivados")
    # Preferimos listar os registros do arquivo tarefas_arquivadas.json (histórico acumulado)
    try:
        with open(TAREFAS_ARQUIVADAS_FILE, "r", encoding="utf-8") as f:
            arquivadas = json.load(f)
    except Exception:
        arquivadas = []

    if not arquivadas:
        print("Nenhuma tarefa arquivada registrada.")
        return

    for a in arquivadas:
        # Não exibir se status é Excluída (registros de arquivamento não deveriam ter excluídas)
        if a.get("status") == "Excluída":
            continue
        print("-" * 50)
        print(f"ID: {a.get('id')}")
        print(f"Título: {a.get('titulo')}")
        print(f"Prioridade: {a.get('prioridade')}")
        print(f"Status: {a.get('status')}")
        print(f"Origem: {a.get('origem')}")
        print(f"Data de Criação: {a.get('creation_date')}")
        print(f"Data de Conclusão: {a.get('completion_date')}")
    print("-" * 50)

def mostrar_menu():
    """
    Exibe o menu principal e solicita a opção do usuário.
    Valida a opção antes de retornar.
    """
    print("Executando a função mostrar_menu")
    print("\n--- Gerenciador de Tarefas ---")
    print("1 - Criar tarefa")
    print("2 - Pegar próxima tarefa (verificação de urgência)")
    print("3 - Atualizar prioridade de tarefa")
    print("4 - Concluir tarefa")
    print("5 - Arquivar tarefas concluídas antigas (forçar limpeza)")
    print("6 - Excluir tarefa (exclusão lógica)")
    print("7 - Relatório completo (todas as tarefas)")
    print("8 - Relatório de arquivados")
    print("9 - Salvar agora")
    print("0 - Sair")
    escolha = input("Escolha uma opção: ").strip()
    return escolha

def salvar_e_sair():
    """
    Salva os dados nos arquivos e encerra o programa usando exit().
    """
    print("Executando a função salvar_e_sair")
    # antes de sair, rodar arquivamento automático para garantir consistência
    arquivar_tarefas_concluidas_antigas()
    salvar_dados()
    print("Dados salvos. Encerrando o programa.")
    exit(0)

# ---------------------------
# Corpo principal do programa
# ---------------------------

def main():
    """
    Fluxo principal do programa: carrega dados, roda arquivamento inicial, e apresenta o menu principal em loop.
    """
    print("Executando a função main")
    carregar_dados()
    # rodar arquivamento inicial automático (regra 5)
    arquivar_tarefas_concluidas_antigas()

    while True:
        opc = mostrar_menu()
        # validar opção
        if opc not in [str(i) for i in range(0,10)]:
            print("Opção inválida. Escolha uma opção entre 0 e 9.")
            continue

        # executar ação conforme opção
        if opc == "1":
            criar_tarefa()
        elif opc == "2":
            verificar_urgencia_e_pegar()
        elif opc == "3":
            atualizar_prioridade()
        elif opc == "4":
            concluir_tarefa()
        elif opc == "5":
            arquivar_tarefas_concluidas_antigas()
        elif opc == "6":
            exclusao_logica()
        elif opc == "7":
            relatorio_completo()
        elif opc == "8":
            relatorio_arquivados()
        elif opc == "9":
            salvar_dados()
            print("Dados salvos.")
        elif opc == "0":
            salvar_e_sair()
        else:
            print("Opção inválida.")  # segurança (não deve chegar aqui)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # garantir salvar antes de sair por Ctrl+C
        print("\nInterrupção detectada (Ctrl+C). Salvando dados antes de sair...")
        salvar_dados()
        sys.exit(0)
