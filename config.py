def load_config(key):
    with open('settings.config') as f:
        lines = f.read().split('\n')
        for line in lines:
            if line.split(';')[0].strip() == key:
                return line.split(':')[1].strip()
