import os

files = os.listdir()
otfs = filter(lambda s: s.endswith('.otf'), files)

font_face = """
@font-face {{
  font-family: '{family}';
  font-style: {style};
  font-weight: {weight};
  src: url('/static/fonts/Ancizar-4.0/{name}') format('truetype');
}}
"""

names = []
with open('ancizar.css', 'w') as file:
    for i, name in enumerate(otfs):

        weight = name.split()[1].split("-")[1].split('.')[0].lower()
        family = name.split("-")[0].replace(' ', '-')
        style = 'italic' if 'Italic' in name else 'normal'
        weight = {
            'light': '400',
            'regular': '500',
            'bold': '700',
            'extrabold': '800',
            'black': '900',
        }[weight]

        file.write(font_face.format(**locals()))
        print(f"{i+1}: {name}")
        names.append(f'{family}-{style}-{weight}')


print('-' * 70)
print(', '.join(names) + ';')
