import random
import mysql.connector
from twilio.rest import Client
from decimal import Decimal
from datetime import datetime

#Log Transcantion
def trans(acc_no, transaction_type, amount, balance):
    try:
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Veeram@50',
            database='pyp'  
        )
        mycursor = mydb.cursor()

        query = 'insert into transactions (acc_no, transaction_type, amount, balance, transaction_date) VALUES (%s, %s, %s, %s, %s)'
        values = (acc_no, transaction_type, amount, balance, datetime.now())
        mycursor.execute(query, values)
        mydb.commit()
        print('Transaction inserted successfully')
        return main()
    except mysql.connector.Error as err:
        print(f'Error: {err}')
        return main()
    finally:
        if 'mycursor' in locals():
            mycursor.close()
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()

    





# Twilio configuration
account_sid = 'ACb08204d89d2853bd40f47723c52b3e4f'
auth_token = 'fdf4bbb82108f61cc45d58433ba987ef'
twilio_phone_number = '+18638374024'

# Function to create account and send OTP
def create_acc():
    name = input("Enter Your Holder Name: ")
    phone_number = input("Enter Your Phone Number: ")

    otp = create_otp()  # Generate OTP
    send_otp(phone_number, otp)  # Send OTP 

    # Verify the OTP
    if verify_otp(otp):
        acc_no = random.randint(1000000000, 1000000099)

        print(f"Account created for {name} with phone number {phone_number} and account number {acc_no}.")

        client = Client(account_sid, auth_token)
        client.messages.create(
            body=f" Hai {name} ,You Have Succesfully Created  Account in Our xyz Bank , And Your Account Number is {acc_no}",
            from_=twilio_phone_number,
            to=phone_number)

        # Initialize database connection
        try:
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='Veeram@50',
                database='pyp'  
            )
            mycursor = mydb.cursor()

            # Insert account details 
            query = "insert into bms (name, acc_no, phone_number, balance) VALUES (%s, %s, %s, %s)"
            values = (name, acc_no, phone_number, 0)
            mycursor.execute(query, values)
            mydb.commit() 

            print("Account details saved to the database successfully.")
            return main()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return main()

        finally:
            # Close
            if 'mycursor' in locals():
                mycursor.close()
            if 'mydb' in locals() and mydb.is_connected():
                mydb.close()
    
    else:
        print("Verification failed. Please try again.")
        return main()

# Function to generate OTP
def create_otp():
    global otp
    otp = random.randint(1000, 9999)
    
    return otp

# Function to send OTP via SMS
def send_otp(phone_number, otp):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"Your OTP is: {otp}",
        from_=twilio_phone_number,
        to=phone_number
    )
    print("OTP sent successfully.")
    return message.sid



# Function to verify the OTP
def verify_otp(sent_otp):
    entered_otp = int(input("Enter the OTP sent to your phone: "))
    if entered_otp == sent_otp:
        print("OTP verified successfully!")
        return True
    else:
        print("Incorrect OTP.")
        return False

def view_balance():
    account_number = int(input("Enter Your Account Number: "))
    try:
        # Initialize the database connection
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Veeram@50',
            database='pyp' 
        )
        mycursor = mydb.cursor()

        
        query = "select balance from bms where acc_no = %s"
        mycursor.execute(query, (account_number,))  

        # Fetch the result
        result = mycursor.fetchone()
        if result:
            balance = result[0]
            print(f"The balance for account number {account_number} is ${balance} , Thankyou Vist Again !")
            return main()
        else:
            print("Account not found , Enter the correct Account Number")
            return main()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return main()
    
    finally:
        # Close 
        if 'mycursor' in locals():
            mycursor.close()
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()
def deposit():
    account_number = int(input("Enter Your Account Number: "))
    deposit_amount = Decimal(input("Enter Amount to Deposit $"))

    try:
        # Initialize the database connection
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Veeram@50',
            database='pyp' 
        )
        mycursor = mydb.cursor()

        # First, check if the account exists and retrieve the current balance
        query = "select balance ,phone_number from bms where acc_no = %s"
        mycursor.execute(query, (account_number,))
        result = mycursor.fetchone()
        
        

        if result:
            # Convert balance to Decimal to ensure both are of the same type
            balance,phone_number = Decimal(result[0]),result[1]
            new_balance = balance + deposit_amount
            

            # Update the balance in the database
            update_query = "update bms set balance = %s where acc_no = %s"
            mycursor.execute(update_query, (new_balance, account_number))
            mydb.commit()  
            print(f"Deposit successful! New balance for account {account_number} is ${new_balance}")
            
            client = Client(account_sid, auth_token)
            client.messages.create(
            body=f"You Have Succesfully Deposited Amount ${deposit_amount} to your Account Number {account_number} and your Balance is $ {new_balance}",
            from_=twilio_phone_number,
            to=phone_number)
            trans(account_number, "Deposit", deposit_amount,new_balance)
            return main()
        else:
            print("Account not found.")
            return main()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return main()
    
    finally:
        
        if 'mycursor' in locals():
            mycursor.close()
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()

def withdraw():
    account_number = int(input("Enter Your Account Number: "))
    withdraw_amount= Decimal(input("Enter the amount to withdraw $"))
    try:
        
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Veeram@50',
            database='pyp'  
        )
        mycursor = mydb.cursor()

         
        query = "select balance , phone_number from bms where acc_no = %s"
        mycursor.execute(query, (account_number,))  

        # Fetch the result
        result = mycursor.fetchone()
        if result :
            balance , phone_number = Decimal(result[0]),result[1]
            print(f"The balance for account number {account_number} is: ${balance}")

            otp = create_otp()  # Generate OTP
            send_otp(phone_number, otp)
            
            if verify_otp(otp):


            
             if balance >= withdraw_amount:
                new_balance = balance-withdraw_amount
                update_querry='update bms set balance =%s where acc_no = %s '
                mycursor.execute(update_querry,(new_balance,account_number))
                mydb.commit()
                print(f"The amount ${withdraw_amount} was Withdraw successfully! New balance for account {account_number} is ${new_balance}")
                client = Client(account_sid, auth_token)
                client.messages.create(
                body=f"You Have Succesfully withdraw Amount ${withdraw_amount}, From your Account Number {account_number} and your Balance is ${new_balance}",
                from_=twilio_phone_number,
                to=phone_number)
                trans(account_number, "Withdraw", withdraw_amount,new_balance)
                return main()
             else:
                print('Insufficient Balance')
                return main()
            else:
                print('Incorrect OTP ')
                return main()
        else:
            print("Account not found.")
            return main()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return main()
    
    finally:
        # Close 
        if 'mycursor' in locals():
            mycursor.close()
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()

def statement():
    account_number = int(input("Enter Your Account Number: "))
    try:
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Veeram@50',
            database='pyp'
        )
        mycursor = mydb.cursor()

        # Retrieve transactions for the account
        query = """
        select transaction_type, amount, balance, transaction_date
        from transactions
        where acc_no = %s
        order by transaction_date asc
        """
        mycursor.execute(query, (account_number,))
        transactions = mycursor.fetchall()

        if transactions:
            print(f"Account Statement for {account_number}:")
            print(f"{'Type':<20} {'Amount':<16} {'Balance':<16} {'Date':<20}")
            print("-" * 60)

            # Loop through each transaction and print it with correct formatting
            for trans in transactions:
                transaction_date, transaction_type, amount, balance = trans
                print(f"{transaction_date:<20} {transaction_type:<15} ${amount:<14,.2f} ${balance}")



            return main()
        else:
            print("No transactions found for this account.")
            return main()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return main()
    
    finally:
        if 'mycursor' in locals():
            mycursor.close()
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()


# Main function
is_running = True
def main():
    global is_running  

    while is_running:
        print('Select 1 for Create Account  \nSelect 2 for Account Exist \nSelect 3 for Exit')
        inpt = int(input('Enter your Input: '))
        
        if inpt == 1:
            create_acc()
        elif inpt == 2:
            print('Select 1 for View Balance \nSelect 2 for Deposit \nSelect 3 for Withdraw \nSelect 4 for Statement')
            inpt1 = int(input('Enter your Input: '))
            
            if inpt1 == 1:
                view_balance()
            elif inpt1 == 2:
                deposit()
            elif inpt1 == 3:
                withdraw()
            elif inpt1 == 4:
                statement()
            else:
                print('Enter a value between 1 and 4.')
        elif inpt == 3:
            print("Exiting...")
            is_running = False  
        else:
            print("Invalid selection. Please enter 1, 2, or 3.")

main()





