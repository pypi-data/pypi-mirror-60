from distutils.core import setup


def read(filename):
    with open(filename, encoding='utf-8') as file:
        return file.read()


setup(
  name='keyboa',
  packages=['keyboa'],
  version='1.0.0',
  license='MIT',
  description="Telegram Inline Keyboards Generator",
  long_description=read('README.md'),
  long_description_content_type="text/markdown",
  author='torrua',
  author_email='torrua@gmail.com',
  url='https://github.com/torrua/keyboa',
  download_url='https://github.com/torrua/keyboa/archive/v1.0.0.tar.gz',
  keywords=['Generate', 'Inline', 'Keyboard', 'Telegram'],
  install_requires=[
          'pytelegrambotapi',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',  # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)
