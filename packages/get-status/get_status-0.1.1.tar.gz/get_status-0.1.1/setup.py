from distutils.core import setup
setup(
  name = 'get_status',
  packages = ['get_status'],
  version = '0.1.1',
  license='MIT',
  description = 'A services who allow you to get the status of any website !',
  author = 'voltis',
  author_email = 'voltis.discord@gmail.com',
  url = 'https://github.com/v0ltis/Get_Status',
  keywords = ['HTTPS', 'WEBSITE', 'SITE','STATUS'],
  install_requires=[
          'requests',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)
