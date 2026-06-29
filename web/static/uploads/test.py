def check_user(user_input):
    query = "SELECT * FROM accounts WHERE name = " + user_input
    eval(user_input)