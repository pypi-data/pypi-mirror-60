import os

files = os.listdir()
otfs = filter(lambda s: s.endswith('.ttf'), files)

font_face = """
@font-face {{
  font-family: '{family}';
  src: url('/static/fonts/ubuntu-font-family-0.83/{name}') format('truetype');
}}
"""

names = []
with open('ubuntu.css', 'w') as file:
    for i, name in enumerate(otfs):

        family = name.split('.')[0]

        file.write(font_face.format(**locals()))
        print(f"{i+1}: {name}")
        names.append(f'{family}')


print('-' * 70)
print(', '.join(names) + ';')
