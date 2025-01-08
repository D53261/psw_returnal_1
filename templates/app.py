import __init__
from views.view import SubscriptionService
from models.database import engine
import models.database
from models.model import Subscription, Users
from datetime import datetime
from decimal import Decimal

class UI:
    def __init__(self):
        self.subscription_service = SubscriptionService(engine)
        self.user = None

    def start(self):
        while True:
            print('''
            [1] -> Adicionar usuário
            [2] -> Selecionar usuário
            [3] -> Excluir usuário
            [4] -> Sair
            ''')
            choice = int(input('Escolha uma opção: '))
            if choice == 1:
                self.add_user()
            elif choice == 2:
                self.select_user()
                if self.user:
                    while True:
                        print('''
                        [1] -> Adicionar assinatura
                        [2] -> Pagar assinatura
                        [3] -> Remover assinatura
                        [4] -> Valor total
                        [5] -> Gastos últimos 12 meses
                        [6] -> Sair do usuário
                        ''')
                        choice = int(input('Escolha uma opção: '))
                        if choice == 1:
                            self.add_subscription()
                        elif choice == 2:
                            self.add_payment()
                        elif choice == 3:
                            self.delete_subscription()
                        elif choice == 4:
                            self.total_value()
                        elif choice == 5:
                            self.subscription_service.gen_chart(self.user.id)
                        else:
                            break
            elif choice == 3:
                self.delete_user()
            else:
                break

    def add_user(self):
        usuario = input('Nome de usuário: ')
        senha = input('Crie uma senha: ')
        user = Users(username=usuario, password=senha)
        self.subscription_service.create_user(user)

    def select_user(self):
        users = self.subscription_service.list_all_users()
        if not users:
            print('Ainda não há usuários cadastrados')
        else:
            usuario = input('Digite o usuário que deseja selecionar: ')
            senha = input('Digite a senha deste usuário: ')
            user = Users(username=usuario, password=senha)
            self.user = self.subscription_service.select_user(user)
            if self.user:
                print('Usuário selecionado com sucesso')
        
    def add_subscription(self):
        empresa = input('Empresa: ')
        site = input('Site: ')
        data_assinatura = datetime.strptime(input('Data de assinatura: '),'%d/%m/%Y')
        valor = Decimal(input('Valor: '))
        subscription = Subscription(empresa=empresa, site=site, data_assinatura=data_assinatura, valor=valor, user_id=self.user.id)
        self.subscription_service.create(subscription)

    def add_payment(self):        
        subscriptions = self.subscription_service.list_all(self.user.id)
        if not subscriptions:
            print('Não há assinaturas pendentes')
        else:
            print('Escolha qual das assinaturas pendentes deseja pagar hoje')

            for i in subscriptions:
                print(f'[{subscriptions.index(i)+1}] -> {i.empresa} / {i.data_assinatura} / {i.valor} / {i.site}')
        
            choice = int(input('Escolha a assinatura: '))
            self.subscription_service.pay(subscriptions[choice-1], self.user.id)

    def delete_subscription(self):
        subscriptions = self.subscription_service.list_all(self.user.id)
        print('Escolha qual assinatura deseja excluir')

        for i in subscriptions:
            print(f'[{i.id}] -> {i.empresa}')

        choice = int(input('Digite o numero referente a assinatura: '))
        self.subscription_service.delete(choice, self.user.id)
        print('Assinatura excluída com sucesso')

    def delete_user(self):
        usuario = input('Digite o usuário que deseja excluir: ')
        senha = input('Digite a senha deste usuário: ')
        user = Users(username=usuario, password=senha)
        self.subscription_service.delete_user(user)
        print('Usuário excluído com sucesso')
    
    def total_value(self):
        print(f'Seu valor total mensal em assinatura é: {self.subscription_service.total_value(self.user.id)}')


if __name__ == "__main__":
    UI().start()

# Para rodar este código(O código da aplicação) deve-se usar o código python templates\app.py