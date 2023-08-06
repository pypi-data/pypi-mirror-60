"""
Programa criado para registro e controle de equipamentos!
Vamos parar de perder equipamento,cacete!!

autor: Felipe Augusto
versao: 1.01
inicio: 23/01/2020
ultima_mod: 23/01/2020
email: fasnik@gmail.com

"""
from datetime import datetime
import os

class Equipamento:

    #Objeto do tipo Equipamento que será usado para gerar
    #relatórios
    
    def __init__(self, dicio):
        self.valores = dicio
        self.item = dicio['item']
        #self.proprietario = vetor['proprietario']
        #self.descricao = vetor['descricao']
        #self.estado = vetor['estado']
        #self.data = vetor['data']
        
    def insereEquip(self):
        #cria chave usando a linha do arquivo
        equip_chave = 1
        try: 
            with open('cadastroEquipamentos.txt') as arqEquip:
                for registro in arqEquip.readlines():
                    equip_chave+=1
        except FileNotFoundError:
            pass
        
        #insere um novo equipamento no final do arquivo        
        with open('cadastroEquipamentos.txt', 'a') as arqEquip:
            arqEquip.write(str(equip_chave))
            arqEquip.write("#")
            for registro in self.valores:
                arqEquip.write(self.valores[registro])
                arqEquip.write("#")
            arqEquip.write('\n')

    def buscaEquip(self, chave_procurada):
        with open('cadastroEquipamentos.txt', 'r') as arqEquip:
            #sentinela indica se a chave foi encontrada
            #evita ter que carregar o arquivo numa lista
            indice = 0
            sentinela = False
            for linha in arqEquip.readlines():
                chave_equip = linha.split('#')[0]
                item_equip = linha.split('#')[1]
                if (item_equip.lower() == chave_procurada.lower() or chave_equip == chave_procurada):
                    sentinela = True
                    break
                else:
                    indice +=1
        return (sentinela,indice)

    def removeEquip(self, indice):
        
        with open('cadastroEquipamentos.txt') as arqEquip:
            with open('cadastro.temp', 'w') as temp:
                cont =0
                for linha in arqEquip.readlines():
                    if indice!=cont:
                        temp.write(linha)
                    cont+=1
        os.rename('cadastro.temp', 'cadastroEquipamentos.txt')
                        
    
    def atualizaEquip(self,indice, dados):
        cont =0
        descritores=["Proprietário", "Descrição", "Estado", "Última atualização"]
        with open('cadastroEquipamentos.txt') as arqEquip:
            for linha in arqEquip.readlines():
                if cont==indice:
                    print("Dados Atuais: ")
                    dados = linha.split("#")
                    print("-------------")
                    print("Item: ", dados[1])
                    print("-------------")
                    for i in range(4):
                        print(descritores[i] ,": " , dados[i+2])
                    break
                cont+=1
            for i in range(3):
                print("--------------")
                dado = input('Atualizar {}? <Enter> para bypass. '.format(descritores[i]))
                if dado!="":
                    dados[i+2] = dado
            dados[5] = datetime.today().strftime("%m/%d/%Y, %H:%M:%S")
            #remove '\n' de dados
            dados.pop()
            print (dados)
            
            with open('cadastroEquipamentos.txt') as arqEquip:
                with open('cadastro.temp', 'w') as temp:
                    cont = 0
                    for linha in arqEquip.readlines():
                        if cont==indice:
                            for registro in dados:
                                temp.write(registro)
                                temp.write("#")
                            temp.write('\n')
                        else:   
                            temp.write(linha)

                        cont+=1

                    
class Relatorio:
    def __init__(self):
        pass

    def gerarRelatorio(self):
        pass


class Usuario:

    #Objeto do tipo Usuario para controle de login
    
    def __init__(self):
        pass

    def atualizaUsuario(self):
        pass

    def removeUsuario(self):
        pass

class janelaTk:
    def __init__(self):
        pass

#Funcao de controle
def controle():

    mensagemInicio = """
    ############################################

    VAMOS PARAR DE PERDER EQUIPAMENTOS, OBRIGADO

    ############################################

    """

    mensagemOpcoes = """
    Escolhe uma opção ai!

    1) Cadastrar equipamento
    2) Atualizar equipamento
    3) Remover equipamento
    4) Salvar relatório
    5) Gerar relatório atual
    6) Gerar relatório geral
    7) Sair

    Opcao >>"""
    
    print(mensagemInicio, end="  ")

    opcao = input(mensagemOpcoes)
    opcoes = {'1':'cadastro', '2':'atualiza', '3':'remove', '4':'salvar',
                   '5':'relatorio', '6':'geral'}
    if opcao in opcoes:
        return [True,opcoes[opcao]]
    if opcao == '7':
        return[False,opcao]
    else:
        return[True, opcao]


def captura_dados_equip(*args):
    print('Identificação: ')
    print('--------------')
        
    item = input("Tipo de Item: ")
    proprietario = input("Proprietário: ")

    print("Caracteristicas: ")
    print('--------------')
    
    descricao = input("Descreva brevemente o equipamento:")
    estado = input("Estado de Funcionamento: ")
    hoje = datetime.today()
    data = hoje.strftime("%m/%d/%Y, %H:%M:%S")

    
    dados = {'item':item, 'proprietario':proprietario,
               'descricao': descricao, 'estado':estado,
               'data':data}
    return dados

#Programa Principal
def main(Opt):
    if Opt == 'cadastro':
        valores = captura_dados_equip()
        #Insere o novo equipamento no arquivo
        novoEquip = Equipamento(valores)
        novoEquip.insereEquip()

        
    elif Opt == 'atualiza':
        item = {'item':input('Atualizar qual equipamento? ')}
        atualizar_equip = Equipamento(item)
        registro_encontrado, indice_equip = atualizar_equip.buscaEquip(item['item'])
        if not registro_encontrado:
            print('Equipamento não listado. Cadastre-o ou use a opção 6!')
        else:
            print('=================================')
            dados= None
            atualizar_equip.atualizaEquip(indice_equip, dados)
            
    elif Opt == 'remove':
        item = {'item':input('Remover qual equipamento? [Digite chave ou item] ')}
        remove_equip = Equipamento(item)
        registro_encontrado, indice_equip = remove_equip.buscaEquip(item['item'])
        if not registro_encontrado:
            print('Equipamento não listado. Use a opção 6!')
        else:
            print('Confimar a remoção de {}?\
[<Enter> = Sim / Caso contrário = Não]'.format(item['item']))
            confirma = input('>>>')
            if confirma == '':
                print('removendo {}'.format(item['item']))
                remove_equip.removeEquip(indice_equip)
            else:
                print('remoção cancelada')
                

    elif Opt == 'salvar':
        pass
    
    elif Opt == 'relatorio':
        pass
    
    elif Opt == 'geral':
        with open('cadastroEquipamentos.txt') as arqEquip:
            print('{:15} {:30} {:10}'.format('Chave','Item','Estado'))
            print('{:15} {:30} {:10}'.format('-----------','----------','---------'))
            for linha in arqEquip.readlines():
                info = linha.split("#")
                print('{:15} {:30} {:10}'.format(info[0],info[1],info[4]))
                      
    else:
        print("""
        ++++++++++++++++++++++++++++++++
        
        Opcao inválida, seu burro!
        Vamos tentar novamente!!!

        ++++++++++++++++++++++++++++++++
        """)

def loopMain(loop = True):
    inloop =loop
    while inloop:
        CONTROLE,OPCAO =controle()
        if CONTROLE:
            main(OPCAO)
        else:
            inloop =False
loopMain()        
#with open('registros.txt', 'a') as REGISTROS:
#    novoRegistro = Relatorio
    
