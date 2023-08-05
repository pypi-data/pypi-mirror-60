import os

files = os.listdir()
otfs = filter(lambda s: s.endswith('.otf'), files)

font_face = """
@font-face {{
  font-family: '{family}';
  src: url('/static/fonts/worksans/{name}') format('truetype');
}}
"""

names = []
with open('worksans.css', 'w') as file:
    for i, name in enumerate(otfs):

        family = name.replace('.otf', '')

        file.write(font_face.format(**locals()))
        print(f"{i+1}: {name}")
        names.append(f'{family}')


print('-' * 70)
print(', '.join(names) + ';')
