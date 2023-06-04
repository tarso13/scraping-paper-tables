# Read elastic password from file given and return it for external use
# File should contain only one line with the password
def get_elastic_password(filename):
    f = open(filename, 'r')
    return f.readline()