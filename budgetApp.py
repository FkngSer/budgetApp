import streamlit as st
import pandas as pd

# Initialize session state
if 'accounts' not in st.session_state:
    st.session_state['accounts'] = pd.DataFrame(columns=['Account Name', 'Balance'])

if 'transactions' not in st.session_state:
    st.session_state['transactions'] = pd.DataFrame(columns=['Type', 'Account', 'Amount', 'Category', 'Date'])


# Function to add account
def add_account(account_name, initial_balance):
    if account_name in st.session_state['accounts']['Account Name'].values:
        st.warning("Account with this name already exists.")
    else:
        new_account = pd.DataFrame({'Account Name': [account_name], 'Balance': [initial_balance]})
        st.session_state['accounts'] = pd.concat([st.session_state['accounts'], new_account], ignore_index=True)


# Function to delete account
def delete_account(account_name):
    st.session_state['accounts'] = st.session_state['accounts'][
        st.session_state['accounts']['Account Name'] != account_name]


# Function to add transaction
def add_transaction(type, account, amount, category, date):
    new_transaction = pd.DataFrame(
        {'Type': [type], 'Account': [account], 'Amount': [amount], 'Category': [category], 'Date': [date]})
    st.session_state['transactions'] = pd.concat([st.session_state['transactions'], new_transaction], ignore_index=True)

    if type == 'Income':
        st.session_state['accounts'].loc[st.session_state['accounts']['Account Name'] == account, 'Balance'] += amount
    elif type == 'Expense':
        st.session_state['accounts'].loc[st.session_state['accounts']['Account Name'] == account, 'Balance'] -= amount
    elif type == 'Transfer':
        source_account, destination_account = account.split(" -> ")
        st.session_state['accounts'].loc[
            st.session_state['accounts']['Account Name'] == source_account, 'Balance'] -= amount
        st.session_state['accounts'].loc[
            st.session_state['accounts']['Account Name'] == destination_account, 'Balance'] += amount


# Streamlit app layout
st.set_page_config(page_title="Budget Tracker", layout="wide")

st.title("Budget Tracker")

# Sidebar for data input
with st.sidebar:
    st.header("Account Management")
    manage_option = st.selectbox("Select Action", ["None", "Add Account", "Delete Account"])

    if manage_option == "Add Account":
        account_name = st.text_input("Account Name")
        initial_balance = st.number_input("Initial Balance", min_value=0.0, step=0.01)
        if st.button("Add Account"):
            add_account(account_name, initial_balance)

    if manage_option == "Delete Account":
        account_to_delete = st.selectbox("Select Account to Delete",
                                         st.session_state['accounts']['Account Name'].tolist())
        if st.button("Delete Account"):
            delete_account(account_to_delete)

    st.header("Add Transaction")
    transaction_type = st.selectbox("Type", ["Income", "Expense", "Transfer"])
    if transaction_type == "Transfer":
        accounts = st.session_state['accounts']['Account Name'].tolist()
        source_account = st.selectbox("Source Account", accounts)
        destination_account = st.selectbox("Destination Account", accounts)
        account = f"{source_account} -> {destination_account}"
    else:
        account = st.selectbox("Account", st.session_state['accounts']['Account Name'].tolist())
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    category = st.text_input("Category")
    date = st.date_input("Date")
    if st.button("Add Transaction"):
        add_transaction(transaction_type, account, amount, category, date)

# Main area for displaying data
st.header("Accounts Overview")
for index, row in st.session_state['accounts'].iterrows():
    st.write(f"**{row['Account Name']}**: {row['Balance']}")

st.header("Transactions Overview")

# Split into two columns
col1, col2 = st.columns([3, 1])

# Apply filters to the transactions dataframe
transaction_filter = st.session_state['transactions'].copy()
columns = transaction_filter.columns.tolist()

with col2:
    st.subheader("Filter Setup")
    selected_columns = st.multiselect("Filter by columns", columns, default=columns)
    if not transaction_filter.empty:
        for column in selected_columns:
            unique_values = transaction_filter[column].unique()
            if len(unique_values) > 1:
                selected_value = st.selectbox(f"Filter {column}", options=["All"] + unique_values.tolist(), key=column)
                if selected_value != "All":
                    transaction_filter = transaction_filter[transaction_filter[column] == selected_value]

with col1:
    st.subheader("Transactions")
    if selected_columns:
        st.table(transaction_filter[selected_columns])  # Use st.table to remove row numbers
    else:
        st.table(transaction_filter)  # Use st.table to remove row numbers
