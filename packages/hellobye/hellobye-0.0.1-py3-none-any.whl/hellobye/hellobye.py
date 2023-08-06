def hello(name, which=1):
    """
    Hello-es a name.
    You can choose from 4 different helloes.
    """
    if which == 1:
        return "Hello %s" % name
    if which == 2:
        return "Hi %s" % name
    if which == 3:
        return "Greetings %s" % name
    if which == 4:
        return "'sup %s" % name
    if which > 4 or which < 1:
        raise ValueError("Hello number %s doesn't exist. There are only 4 helloes." % which)
    if name is None:
        raise Exception("You need someone to say hello to.")


def bye(name, which=1):
    """
    Bye-s a name.
    You can choose from 4 different byes.
    """
    if which == 1:
        return "Bye %s" % name
    if which == 2:
        return "Goodbye %s" % name
    if which == 3:
        return "Take Care %s" % name
    if which == 4:
        return "See you soon %s" % name
    if which > 4 or which < 1:
        raise ValueError("Bye number %s doesn't exist. There are only 4 byes." % which)
    if name is None:
        raise Exception("You need someone to say bye to.")
