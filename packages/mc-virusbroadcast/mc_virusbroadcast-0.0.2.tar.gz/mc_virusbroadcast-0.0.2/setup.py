from setuptools import setup

setup(
    name='mc_virusbroadcast',
    version='0.0.2',
    author='Hugn',
    author_email='wang1183478375@outlook.com',
    url ='https://www.coding4fun.com.cn/',
    install_requires=['pygame>=1.9.4',
                      'numpy>=1.18.1'
                      ],
    data_files=[('',['Bed.py']),
                ('',['City.py']),
                ('',['Constants.py']),
                ('',['Hospital.py']),
                ('',['Main.py']),
                ('',['MoveTarget.py']),
                ('',['MyPanel.py']),
                ('',['Person.py']),
                ('',['PersonPool.py']),
                ('',['Point.py']),
                ('',['Virus.py']),
                ('',['VirusBroadcast.py'])
                ],
    include_package_data = True, 
    zip_safe=False,
    )