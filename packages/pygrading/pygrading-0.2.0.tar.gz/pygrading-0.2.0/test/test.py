from pygrading.html import *

# 由于input()为Python内置方法，故创建<input>标签的方法为`input_tag()`
result = form(
    font().set_text("First name"),
    br(),
    input_tag(type="text", name="firstname"),
    br(),
    font().set_text("Last name"),
    br(),
    input_tag(type="text", name="lastname"),
    br(),
    input_tag(type="submit", value="Submit")
)

result.print()
