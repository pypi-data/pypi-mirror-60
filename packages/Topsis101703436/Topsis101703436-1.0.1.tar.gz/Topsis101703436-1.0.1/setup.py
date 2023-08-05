from setuptools import setup
  
setup( 
        name ='Topsis101703436', 
        version ='1.0.1', 
        author ='Ranveer Singh', 
        author_email ='donotreply@gmail.com', 
        description ='UCS633 Assignment - Topsis', 
        license ='MIT', 
        packages = ["Topsis"],
        entry_points ={ 
            'console_scripts': [ 
                'topsis = Topsis.main:cmd_topsis'
            ] 
        },
        keywords ='thapar ucs633 assignment majboori'
) 