import __init__
from models.database import engine
from models.model import Subscription, Payments, Users
from sqlmodel import Session, select
from datetime import date, datetime

class SubscriptionService:
    def __init__(self, engine):
        self.engine = engine

    def create_user(self, users: Users):
        with Session(self.engine) as session:
            session.add(users)
            session.commit()
            return users
        
    def select_user(self, users: Users):
        with Session(self.engine) as session:
            statement = select(Users).where(Users.username == users.username, Users.password == users.password)
            user = session.exec(statement).one_or_none()
            if user is None:
                print('Usuário não encontrado')
                return None
            return user
        
    def list_all_users(self):
        with Session(self.engine) as session:
            statement = select(Users)
            results = session.exec(statement).all()
        return results
    
    def delete_user(self, user: Users):
        with Session(self.engine) as session:
            statement1 = select(Users).where(Users.username == user.username, Users.password == user.password)
            result1 = session.exec(statement1).one_or_none()
            if result1 is None:
                print('Usuário não encontrado')
                return
            statement2 = select(Subscription).where(Subscription.user_id == result1.id)
            result2 = session.exec(statement2).all()
            statement3 = select(Payments).where(Payments.user_id == result1.id)
            result3 = session.exec(statement3).all()
            for subscription in result2:
                session.delete(subscription)
            for payment in result3:
                session.delete(payment)
            session.delete(result1)
            session.commit()

    def create(self, subscription: Subscription):
        with Session(self.engine) as session:
            session.add(subscription)
            session.commit()
            return subscription
        
    def list_all(self, user_id):
        with Session(self.engine) as session:
           statement = select(Subscription).where(Subscription.user_id == user_id)
           results = session.exec(statement).all()
        return results 
    
    def delete(self, id, user_id):
        with Session(self.engine) as session:
            statement = select(Subscription).where(Subscription.id == id and Subscription.user_id == user_id)
            result = session.exec(statement).one()
            pagamentos = session.exec(select(Payments).where(Payments.subscription_id == id and Payments.user_id == user_id)).all()
            for pagamento in pagamentos:
                pagamento.state = "Cancelado"
            session.delete(result)
            session.commit()
    
    def _has_pay(self, results, user_id):
        for result in results:
            if result.date.month == date.today().month and result.user_id == user_id:
                return True
        return False

    def pay(self, subscription: Subscription, user_id):
        with Session(self.engine) as session:
            statement = select(Payments).join(Subscription).where(Subscription.empresa == subscription.empresa and Subscription.user_id == subscription.user_id)
            results = session.exec(statement).all()

            if self._has_pay(results, user_id):
                question = input("Essa conta já foi paga esse mês, deseja pagar novamente? (Y ou N): ")

                if not question.upper() == 'Y':
                    return 
                
            pay = Payments(subscription_id=subscription.id, date = date.today(), user_id=user_id)
            session.add(pay)
            session.commit()
            print('Assinatura paga com sucesso')

    def total_value(self, user_id):
        with Session(self.engine) as session:
            statement = select(Subscription).where(Subscription.user_id == user_id)
            results = session.exec(statement).all()

        total = 0
        for result in results:
            total += result.valor

        return float(total)
    
    def _get_last_12_months_native(self):
        today = datetime.now()
        year = today.year
        month = today.month
        last_12_month = []
        for i in range(12):
            last_12_month.append((month, year))
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        
        return last_12_month[::-1]
    
    def _get_values_for_months(self, last_12_months, user_id):
        with Session(self.engine) as session:
            statement = select(Payments).where(Payments.user_id == user_id)
            results = session.exec(statement).all()

            value_for_months = []
            for i in last_12_months:
                value = 0
                for result in results:
                    if result.date.month == i[0] and result.date.year == i[1] and result.state == "Funcional":
                        value += float(result.subscription.valor)
                value_for_months.append(value)
            return value_for_months

    def gen_chart(self, user_id):
        last_12_months = self._get_last_12_months_native()
        value_for_months = self._get_values_for_months(last_12_months, user_id)
        last_12_months = list(map(lambda x: x[0], self._get_last_12_months_native()))
        import matplotlib.pyplot as plt

        plt.plot(last_12_months, value_for_months)
        plt.show()
