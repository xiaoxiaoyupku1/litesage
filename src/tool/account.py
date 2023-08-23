"""
Level 1 User: unregistered users
    can only simulate netlists with Standard components
Level 2 User: registered users
    can simulate netlists with Standard & PDK components
Level 3 User: registered and authenticated users
    can simulate netlists with Standard, PDK & IP components
All users can draw schematics with all kinds of components.
"""

class UserAccount():
    def __init__(self):
        self.level = 1

        self.name = ""      # string: user name
        self.phone = ""     # string: length = 11
        self.passwd = ""    # string: any string
        self.org = ""       # string: school, company
        self.role = ""      # string: student, engineer, designer

    def getLevel(self):
        return self.level

    def update(self, name, phone, passwd, org, role):
        self.name = name
        self.phone = phone
        self.passwd = passwd
        self.org = org
        self.role = role
        if len(org) > 0 and len(role) > 0:
            self.level = 3
        else:
            self.level = 2