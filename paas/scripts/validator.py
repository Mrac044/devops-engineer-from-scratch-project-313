def validate(link):

    if not isinstance(link, dict):
        return {"payload": "Invalid data format"}

    errors = {}
    if not link.get('original_url'):
        errors['original_url'] = "Can't be blank"

    if not link.get('short_name'):
        errors['short_name'] = "Can't be blank"

    elif '/' in link.get('short_name') or ':' in link.get('short_name'):
        errors['special_symbols'] = "Can't be special symbols"

    return errors
