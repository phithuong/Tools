# Save data to session
def save_session(request, **kwargs):
    for key, value in kwargs.items():
        request.session[key] =  value


# Get data from session
def get_session(request, key=None):
    if key is not None:
        value = request.session.get(key)
    else:
        value = request.session
    return value

# Remove data from session
def remove_session(request, key=None):
    if key in request.session:
        del request.session[key]
    return 0