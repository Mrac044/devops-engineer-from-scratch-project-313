def validate(link):
    errors = {}
    if not link.get('original_url'):
        errors['original_url'] = "Can't be blank"
    if '/' in link['short_name'] or ':' in link['short_name']:
        errors['special_symbols'] = "Can't be special symbols"
    if not link.get('short_name'):
        errors['short_name'] = "Can't be blank"
    
    return errors