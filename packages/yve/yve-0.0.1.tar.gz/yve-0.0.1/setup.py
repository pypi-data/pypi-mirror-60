from setuptools import setup#, find_packages

LONGDOC = '''
All respect to 'DQinYuan'
这个就是一个可以把字符串文本里面的地址解析出来并生成一个DataFrame的小包.
用法：
import yve_help
yve_help.transform(location_list)
注意一定是list啊

Dedicate this package to Yve and I love her
 '''


requires = ['pandas(>=0.20.0)',
            'jieba(>=0.39)',
            ]

setup(name='yve',
      version='0.0.1',
      description='Chinese Province, City and Area Recognition Utilities',
      long_description=LONGDOC,
      author='Hugh',
      license="MIT",
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python :: 3.6',
          'Topic :: Text Processing',
          'Topic :: Text Processing :: Indexing',
      ],
      keywords='for study',
      packages=['mapper',''],
      package_dir={'mapper': 'mapper','': '.', },
      install_requires=requires)