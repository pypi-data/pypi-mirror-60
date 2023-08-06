from prompt_toolkit import prompt

def hide(input=""):
    if input == "":
       return
    return prompt(unicode(input),is_password=True)
