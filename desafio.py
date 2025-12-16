from datetime import datetime
#datetime.now()

clientes = []
contas = []

nro_conta = 1
NRO_AGENCIA = '0001'

menu = """
[1] Cadastrar cliente
[2] Criar conta
[3] Depositar
[4] Sacar
[5] Extrato
[6] Listar Contas
[0] Sair

=> """

class ContaIterador:
    def __init__(self, contas):
        self.contas = contas
        self.contador = 0

    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            conta = self.contas[self.contador]

            if not conta:
                return

            self.contador += 1
            return conta        
        except IndexError:
            raise StopIteration

def log_transacao(funcao):
    def envelope(*args, **kwargs):
        tipo_transacao = funcao.__name__
        tipo_transacao = tipo_transacao.replace('_', ' ').title()
        
        resultado = funcao(*args, **kwargs)

        if resultado:
            print("\n=================== Log ===================")
            print(f"Ação realizada às {datetime.now().strftime("%H:%M:%S (%d/%m/%Y)")}")
            print(f"Tipo: {tipo_transacao}")
            print("===========================================")
        return resultado
    
    return envelope

@log_transacao
def sacar(*, cpf, valor):
    contas_cliente = []
    numeros_contas = []
    for conta in contas:
        if conta['cpf'] == cpf:
            contas_cliente.append(conta)
            numeros_contas.append(conta['nro'])
    
    if numeros_contas:
        print("Contas que o cliente possui: ", numeros_contas)
        conta_alvo = input("Informe o nro da conta para o saque: ")
    else:
        print("Cliente ainda não possui uma conta cadastrada!")
        return

    while(1):
        if conta_alvo not in numeros_contas:
            print('Opção inválida. Contas que o cliente possui: ', numeros_contas)
            conta_alvo = input("Informe o nro da conta que receberá saque: ")
            continue
        else:
            break
    
    for conta in contas_cliente:
        if conta_alvo == conta['nro']:
            excedeu_saldo = valor > conta['saldo']
            excedeu_limite = valor > conta['limite']
            excedeu_saques = conta['numero_saques'] >= conta['limite_saques']

            if excedeu_saldo:
                print("Operação falhou! Conta sem saldo suficiente.")
                break
            elif excedeu_limite:
                print("Operação falhou! O valor excede o limite permitido para saques.")
            elif excedeu_saques:
                print("Operação falhou! Número máximo de saques excedido.")
            else:
                conta['saldo'] -= valor

                registro_operacao = {
                    'tipo': "saque",
                    'log': f"- Saque: R$ {valor:.2f} - {datetime.now().strftime("%H:%M:%S (%d/%m/%Y)")}"
                }

                conta['extrato'].append(registro_operacao)
                conta['numero_saques'] += 1
                print("\nOperação realizada com sucesso!")
                print(f"Novo saldo: R$ {conta['saldo']:.2f}")
    return 1

@log_transacao
def depositar(cpf, valor, /):
    contas_cliente = []
    numeros_contas = []
    for conta in contas:
        if conta['cpf'] == cpf:
            contas_cliente.append(conta)
            numeros_contas.append(conta['nro'])
    
    if numeros_contas:
        print("Contas que o cliente possui: ", numeros_contas)
        conta_alvo = input("Informe o nro da conta para o depósito: ")
    else:
        print("Cliente ainda não possui uma conta cadastrada!")
        return

    while(1):
        if conta_alvo not in numeros_contas:
            print('Opção inválida. Contas que o cliente possui: ', numeros_contas)
            conta_alvo = input("Informe o nro da conta que receberá o deposito: ")
            continue
        else:
            break
    
    for conta in contas_cliente:
        if conta_alvo == conta['nro']:
            conta['saldo'] += valor

            registro_operacao = {
                'tipo': "deposito",
                'log': f"- Depósito: R$ {valor:.2f} - {datetime.now().strftime("%H:%M:%S (%d/%m/%Y)")}"
            }
            conta['extrato'].append(registro_operacao)

            print("\nOperação realizada com sucesso!")
            print(f"Novo saldo: R$ {conta['saldo']:.2f}")
    return 1

@log_transacao
def obter_extrato(saldo, /, *, extrato):
    print("\n================ Histórico ================")

    if not extrato:
        print("Não foram realizadas movimentações.")
    else: 
        for operacao in extrato:
            yield operacao

    print(f"\nSaldo atual: R$ {saldo:.2f}")
    print("==========================================")
    return 1

@log_transacao
def cadastrar_cliente(nome, data_nascimento, cpf, endereco):
    novo_cliente = {
        "nome": nome,
        "data_nascimento": data_nascimento,
        "cpf": cpf,
        "endereco": endereco
    }

    clientes.append(novo_cliente)
    return 1

@log_transacao
def criar_conta_corrente(agencia, nro_conta, cpf, nome_titular):
    nova_conta = {
        "agencia": agencia,
        "nro": nro_conta,
        "nome_titular": nome_titular,
        "cpf": cpf,
        "saldo": 0,
        "limite": 500,
        "numero_saques": 0,
        "limite_saques": 3,
        "extrato": []
    }
    
    contas.append(nova_conta)
    return 1
    

def definir_nascimento():
    data_nascimento = input("Informe a data de nascimento do cliente no formato DD/MM/AAAA: ")
        
    while(1):
        aux = []
        aux = data_nascimento.split('/')

        if not len(aux) == 3:
            data_nascimento = input("Data inválida. Digite a data de nascimento do cliente no formato DD/MM/AAAA: ")
            continue

        erro = False
        for item in aux:
            if not item.isdigit():
                print(item, "não é um valor válido para datas.")
                erro = True
                break
        
        if erro:
            data_nascimento = input("Digite a data de nascimento do cliente no formato DD/MM/AAAA: ")
            continue
        
        dia = int(aux[0])
        mes = int(aux[1])
        ano = int(aux[2])

        if not (1 <= dia <= 31):
            print(aux[0],"não é um dia válido.")
            data_nascimento = input("Digite a data de nascimento do cliente no formato DD/MM/AAAA: ")
            continue

        if not (1 <= mes <= 12):
            print(aux[1],"não é um mês válido.")
            data_nascimento = input("Digite a data de nascimento do cliente no formato DD/MM/AAAA: ")
            continue

        if ano < 1900 or ano > 2010:
            print("Novos clientes não podem ter menos de 16 anos ou terem nascido antes de 1900!")
            return None
        
        break

    return data_nascimento


def definir_cpf():
    cpf = input("Informe o CPF do cliente (apenas números): ")

    while(1):

        if not cpf.isdigit():
            cpf = input('Digite apenas números para o CPF. Tente novamente: ')
            continue

        if len(cpf) != 11:
            cpf = input('O CPF deve conter 11 dígitos. Tente novamente: ')
            continue

        if consultar_cpf(cpf):
            cpf = input('Já existe um cliente cadastrado com o CPF informado. Tente novamente: ')
            continue

        break
    return cpf


def consultar_cpf(cpf):

    if len(clientes) == 0:
        return False
    
    for item in clientes:
        if item['cpf'] == cpf:
            return item['nome']
        
    return False


def ler_valor():
    while(1):
        try:
            valor = float(input("Informe o valor: "))
            if valor > 0:
                return valor
            else:
                print("O valor deve ser maior que zero.")
        except ValueError:
            print("Operação falhou! O valor informado é inválido! Digite apenas números e separe casa decimal com ponto (ex.: 1150.50)")


def selecionar_conta(cpf):
    contas_cliente = []
    numeros_contas = []
    for conta in contas:
        if conta['cpf'] == cpf:
            contas_cliente.append(conta)
            numeros_contas.append(conta['nro'])
    
    while(1):
        if numeros_contas:
            print("Contas que o cliente possui: ", numeros_contas)
            conta_alvo = input("Informe o nro da conta para a operação: ")
            
            if conta_alvo not in numeros_contas:
                print('Opção inválida.')
                continue
            else:
                for conta in contas_cliente:
                    if conta['nro'] == conta_alvo:
                        return conta
        else:
            print("Cliente ainda não possui uma conta cadastrada!")
            return

while True:

    opcao = input(menu)

    if opcao == '1':
        endereco = ''
        nome = input("Informe o nome do cliente: ")
        data_nascimento = definir_nascimento()
        
        if data_nascimento is None:
            continue

        cpf = definir_cpf()
        endereco += input('Informe o logradouro do cliente: ')
        endereco += ', ' + input('Informe o número da casa do cliente: ')
        endereco += ' - ' + input('Informe a cidade do cliente: ')
        endereco += '/' + input('Informe a sigla do estado: ')

        cadastrar_cliente(nome, data_nascimento, cpf, endereco)

    elif opcao == '2':
        cpf = input("Informe o CPF do cliente: ")

        cliente = consultar_cpf(cpf)
        if cliente == False:
            print("CPF inválido ou não cadastrado!")
            continue

        criar_conta_corrente(NRO_AGENCIA, str(nro_conta), cpf, cliente)
        nro_conta += 1
    
    elif opcao == "3":
        cpf = input("Informe o CPF do cliente: ")

        cliente = consultar_cpf(cpf)
        if cliente == False:
            print("CPF inválido ou não cadastrado!")
            continue

        valor = ler_valor()
        depositar(cpf, valor)

    elif opcao == "4":
        cpf = input("Informe o CPF do cliente: ")

        cliente = consultar_cpf(cpf)
        if cliente == False:
            print("CPF inválido ou não cadastrado!")
            continue

        valor = ler_valor()
        sacar(cpf = cpf, valor = valor)

    elif opcao == "5":
        cpf = input("Informe o CPF do cliente: ")

        cliente = consultar_cpf(cpf)
        if cliente == False:
            print("CPF inválido ou não cadastrado!")
            continue

        conta = selecionar_conta(cpf)

        if conta is None:
            continue

        while(1):
            try:
                print("\nOpções: \n[1] - Ver Depósitos\n[2] - Ver Saques\n[3] - Todas")
                opcao_escolhida = int(input("Informe o tipo de transação que deseja conferir: "))
                if opcao_escolhida in [1, 2, 3]:
                    break
                else:
                    print("Opção inválida!")
            except ValueError:
                print("Opção inválida!")

        for operacao in obter_extrato(conta['saldo'], extrato = conta['extrato']):
            if opcao_escolhida == 1:
                if operacao['tipo'] == 'deposito':
                    print(operacao['log'])
            elif opcao_escolhida == 2:
                if operacao['tipo'] == 'saque':
                    print(operacao['log'])
            else:
                print(operacao['log'])

    elif opcao == "6":
        if not contas:
            print("---------------------------")
            print("Nenhuma conta cadastrada...")
            print("---------------------------")

        for conta  in ContaIterador(contas):
            print("--------------------------")
            print(f"Titular: {conta['nome_titular']}")
            print(f"AG: {conta['agencia']}")
            print(f"C/C: {conta['nro']}")
            print(f"Saldo: R$ {conta['saldo']:.2f}")
            print("--------------------------")

    elif opcao == "0":
        break

    else:
        print("Operação inválida, por favor selecione novamente a operação desejada.")