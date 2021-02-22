# This program is intro to card banking system and has a following features:
# - creating card number and pin in SQL
# - adding income and transferring to other accounts
# - deleting account - removing from data base
# Author: Mateusz Gąsior

import random
import sqlite3


class BankingSystem:

    def __init__(self):
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        self.counter = 0
        self.create_table()
        self.menu()

    def create_table(self) -> None:
        self.cur.execute('''CREATE TABLE IF NOT EXISTS card(
                        id              INTEGER,
                        number          TEXT UNIQUE,
                        pin             TEXT,
                        balance         INTEGER DEFAULT 0
                        );
                        ''')
        self.conn.commit()

    def menu(self) -> None:
        while True:
            print("1. Create an account\n2. Log into account\n0. Exit")
            user_choice = int(input(">"))
            if user_choice == 1:
                self.create_account()
            elif user_choice == 2:
                self.login()
            elif user_choice == 0:
                print("Bye!")
                self.conn.close()
                exit()
            else:
                print("Unknown value")

    def create_account(self) -> None:
        card_number, pin_number = next(self.generate_numbers())
        self.counter = self.create_id()
        self.cur.execute("INSERT INTO card VALUES (?, ?, ?, ?)", (self.counter, card_number, pin_number, 0))
        self.conn.commit()
        print('\nYour card has been created')
        print(f'Your card number:\n{card_number}')
        print(f'Your card PIN:\n{pin_number}\n')

    def account(self, card: str) -> None:
        while True:
            print('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')
            choice = input('>')
            self.cur.execute("SELECT balance FROM card WHERE number=:card", {"card": card})
            balance = self.cur.fetchall()[0][0]
            if choice == '1':
                print(f"\nBalance: {balance}\n")
            elif choice == '2':
                self.add_income(balance, card)
            elif choice == '3':
                self.do_transfer(balance, card)
            elif choice == '4':
                self.close_account(card)
            elif choice == '5':
                print('You have successfully logged out!\n')
                return
            elif choice == '0':
                print('Bye!')
                self.conn.close()
                exit()
            else:
                print('Unknown option.\n')

    def login(self) -> None:
        card = input('Enter your card number:\n')
        PIN = input('Enter your PIN:\n')
        try:
            self.cur.execute('SELECT number, pin FROM card WHERE number=:card and pin=:pin', {"card": card, "pin": PIN})
            user_data = self.cur.fetchall()
            if user_data[0][1] == PIN:
                print('You have successfully logged in!\n')
                self.account(card)
            else:
                print('Wrong card number or PIN\n')
        except IndexError:
            print('Wrong card number or PIN\n')

    def add_income(self, balance, card):
        print('Enter income:')
        income = int(input('>'))
        balance += income
        self.cur.execute('UPDATE card SET balance = ? WHERE number = ?', (balance, card))
        self.conn.commit()
        print("Income was added!")

    def do_transfer(self, balance: int, card: int) -> None:
        print("Transfer\nEnter card number:")
        trans_to = input('>')
        if self.creating_with_luna(trans_to[:15]) == trans_to:
            self.cur.execute('SELECT balance FROM card WHERE number=:card', {"card": trans_to})
            sent_user = self.cur.fetchall()
            if sent_user:
                print("Enter how much money you want to transfer:")
                money = int(input('>'))
                if balance < money:
                    print("Not enough money!")
                else:
                    execution_line = 'UPDATE card SET balance = ? WHERE number = ?'
                    self.cur.execute(execution_line, (balance - money, card))
                    self.cur.execute(execution_line, (sent_user[0][0] + money, trans_to))
                    self.conn.commit()
            else:
                print("Such a card does not exist.")
        else:
            print("Probably you made a mistake in the card number. Please try again!")

    def close_account(self, card: int) -> None:
        self.cur.execute('DELETE FROM card WHERE number = ?', (card,))
        self.conn.commit()
        print("The account has been closed!")
        self.menu()

    @staticmethod
    def generate_numbers() -> tuple:
        global random_card
        while True:
            # In this case luhna algorithm is used, can't be changed by a user
            luna = True
            if luna:
                random_card_front = '400000' + ''.join([str(n) for n in random.sample(range(10), 9)])
                random_card = BankingSystem.creating_with_luna(random_card_front)
            else:
                random_card_front = '400000' + ''.join([str(n) for n in random.sample(range(10), 10)])

            random_pin = ''.join([str(n) for n in random.sample(range(10), 4)])
            yield random_card, random_pin

    @staticmethod
    def creating_with_luna(card_front: str) -> str:
        check_sum = 0
        front_number = list(card_front)
        for i in range(len(front_number)):
            number = int(front_number[i])
            if i % 2 == 0 and number * 2 > 9:
                check_sum += number * 2 - 9
            elif i % 2 == 0 and number * 2 <= 9:
                check_sum += number * 2
            else:
                check_sum += number

        random_card_back = str(10 - check_sum % 10 if check_sum % 10 != 0 else 0)
        return card_front + random_card_back

    def create_id(self) -> int:
        self.cur.execute("SELECT count(*) FROM card")
        record = self.cur.fetchall()
        try:
            return record[0][0] + 1
        except IndexError:
            return 1


if __name__ == "__main__":
    BankingSystem().menu()
