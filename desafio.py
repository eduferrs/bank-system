from datetime import datetime
from abc import ABC, abstractmethod
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


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
    
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, endereco, cpf, nome, data_nascimento):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento

class Conta:
    def __init__(self, agencia, nro, cliente):
        self._saldo = 0
        self._nro = nro
        self._agencia = agencia
        self._cliente = cliente
        self._historico = Historico()
    
    @property
    def saldo(self):
        return self._saldo

    @property
    def nro(self):
        return self._nro
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico
    
    def sacar(self, valor):
        if valor > self._saldo:
            return False
        
        self._saldo -= valor
        return True
    
    def depositar(self, valor):
        self._saldo += valor
        return True
    
    def __str__(self):
        return f"{'='*25}\nTitular: {self.cliente.nome}\nAG: {self.agencia}\nC/C: {self.nro}"

class ContaCorrente(Conta):
    def __init__(self, agencia, nro, cliente):
        super().__init__(agencia, nro, cliente)
        self.limite = 500
        self.limite_saques = 3
        self.saques_realizados = 0

    def sacar(self, valor):
        excedeu_saldo = valor > self.saldo
        excedeu_limite = valor > self.limite
        excedeu_saques = self.saques_realizados >= self.limite_saques

        if excedeu_saldo:
            print("Operação falhou! Conta sem saldo suficiente.")
            return False
        elif excedeu_limite:
            print("Operação falhou! O valor excede o limite permitido para saques.")
            return False
        elif excedeu_saques:
            print("Operação falhou! Número máximo de saques excedido.")
            return False
        else:
            self.saques_realizados += 1
            return super().sacar(valor)
    

class Historico:
    def __init__(self):
        #Mantendo privado (historico em Conta está privado)
        self._transacoes = []
    
    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        
        info = {
            'tipo': f"{transacao.__class__.__name__}",
            'valor': f"R$ {transacao.valor:.2f}",
            'data': f"{datetime.now().strftime("%H:%M:%S (%d/%m/%Y)")}"
        }
        self.transacoes.append(info)


class Transacao(ABC):
    @abstractmethod
    def registrar(self, conta):
        pass

    @property
    @abstractmethod
    #transacoes em Historico está privado
    def valor(self):
        pass


class Deposito(Transacao):
    def __init__(self, valor):
        super().__init__()
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso = conta.depositar(self.valor)

        if sucesso:
            conta.historico.adicionar_transacao(self)


class Saque(Transacao):
    def __init__(self, valor):
        super().__init__()
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso = conta.sacar(self.valor)

        if sucesso:
            conta.historico.adicionar_transacao(self)
            return True
        else:
            return False


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
def sacar(*, conta, valor):
    
    transacao = Saque(valor)
    sucesso = transacao.registrar(conta)
    
    if sucesso:
        return True
    else:
        return False


@log_transacao
def depositar(conta, valor, /):
    transacao = Deposito(valor)
    transacao.registrar(conta)
    return True


@log_transacao
def exibir_extrato(conta):
    print("\n================ Histórico ================")

    if not conta.historico.transacoes:
        print("Não foram realizadas movimentações.")
    else: 
        for transacao in conta.historico.transacoes:
            yield transacao

    print(f"\nSaldo atual: R$ {conta.saldo:.2f}")
    print("==========================================")
    return 1


@log_transacao
def cadastrar_cliente(nome, data_nascimento, cpf, endereco):
    clientes.append(PessoaFisica(endereco, cpf, nome, data_nascimento))
    return 1


@log_transacao
def criar_conta_corrente(agencia, nro_conta, cliente):
    nova_conta = ContaCorrente(agencia, nro_conta, cliente)
    cliente.adicionar_conta(nova_conta)
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
            print("Novos clientes não podem ter menos que 16 anos ou terem nascido antes de 1900!")
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
    
    for cliente in clientes:
        if cliente.cpf == cpf:
            return cliente
        
    return False


def ler_valor():
    while(1):
        try:
            valor = float(input("Informe o valor (ou 0 para cancelar): "))
            if valor > 0:
                return valor
            elif valor == 0:
                return False
            else:
                print("O valor não pode ser menor que zero!")
        except ValueError:
            print("O valor informado é inválido! Digite apenas números e separe casa decimal com ponto (ex.: 1150.50)")


def selecionar_conta(cliente):    
    while(1):
        if cliente.contas:
            print("Contas que o cliente possui:")
            print('\n'.join(str(conta) for conta in cliente.contas))

            conta_alvo = input("Informe o nro da conta (ou 0 para cancelar): ")
            
            if conta_alvo == '0':
                print('Ação cancelada...')
                return False
            
            for conta in cliente.contas:
                if conta_alvo == conta.nro:
                    return conta
            
            print('Opção inválida!\n')
            continue                 
        else:
            print("Cliente ainda não possui uma conta cadastrada!")
            return False


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

        criar_conta_corrente(NRO_AGENCIA, str(nro_conta), cliente)
        nro_conta += 1  
    
    elif opcao == "3":
        cpf = input("Informe o CPF do cliente: ")

        cliente = consultar_cpf(cpf)
        if cliente == False:
            print("CPF inválido ou não cadastrado!")
            continue
        
        conta = selecionar_conta(cliente)
        if conta == False:
            continue

        valor = ler_valor()
        if valor == False:
            continue

        depositar(conta, valor)

    elif opcao == "4":
        cpf = input("Informe o CPF do cliente: ")

        cliente = consultar_cpf(cpf)
        if cliente == False:
            print("CPF inválido ou não cadastrado!")
            continue
        
        conta = selecionar_conta(cliente)
        if conta == False:
            continue

        valor = ler_valor()
        if valor == False:
            continue

        sacar(conta=conta, valor=valor)

    elif opcao == "5":
        cpf = input("Informe o CPF do cliente: ")

        cliente = consultar_cpf(cpf)
        if cliente == False:
            print("CPF inválido ou não cadastrado!")
            continue

        conta = selecionar_conta(cliente)
        if conta == False:
            continue

        while(1):
            try:
                print("\nOpções: \n[1] Ver Depósitos\n[2] Ver Saques\n[3] Todas")
                opcao_escolhida = int(input("Informe o tipo de transação que deseja conferir: "))
                if opcao_escolhida in [1, 2, 3]:
                    break
                else:
                    print("Opção inválida!")
            except ValueError:
                print("Opção inválida!")

        for transacao in exibir_extrato(conta):
            if opcao_escolhida == 1:
                if transacao['tipo'] == 'Deposito':
                    print(f'{transacao['tipo']} {transacao['valor']} - {transacao['data']}')
            elif opcao_escolhida == 2:
                if transacao['tipo'] == 'Saque':
                    print(f'{transacao['tipo']} {transacao['valor']} - {transacao['data']}')
            else:
                print(f'{transacao['tipo']} {transacao['valor']} - {transacao['data']}')

    elif opcao == "6":
        if not clientes:
            print("---------------------------")
            print("Nenhum cliente cadastradado...")
            print("---------------------------")
            continue
        
        if not contas:
            print("---------------------------")
            print("Nenhuma conta cadastrada...")
            print("---------------------------")
            continue

        for conta in ContaIterador(contas):
            print(conta)
            print(f"Saldo: R$ {conta.saldo:.2f}")

    elif opcao == "0":
        break

    else:
        print("Operação inválida, por favor selecione novamente a operação desejada.")