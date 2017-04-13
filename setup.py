from setuptools import setup, find_packages  



setup(  
    name='nata',  
    version='0.1',  
    packages=find_packages(),  
    entry_points={  
        'console_scripts':  
            'nata = nata.cli:main'  
    },  
    zip_safe=False,  
    test_suite = 'tests',
    classifiers=[  
          'Environment :: Console',  
          'Intended Audience :: Developers',  
          'Programming Language :: Python',  
          'Programming Language :: Python :: 2.7',  
    ],  
)  

