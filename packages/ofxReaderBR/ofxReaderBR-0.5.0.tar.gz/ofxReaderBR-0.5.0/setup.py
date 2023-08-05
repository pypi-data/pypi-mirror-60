from distutils.core import setup

setup(
    name='ofxReaderBR',  # How you named your package folder (MyLib)
    packages=['ofxReaderBR',
              'ofxReaderBR.factory',
              'ofxReaderBR.model',
              'ofxReaderBR.reader',
              'ofxReaderBR.reader.pdf',
              'ofxReaderBR.writer',
              'ofxReaderBR.writer.xlsm',
              'ofxReaderBR.writer.bankstatement',
              'ofxReaderBR.utils'],  # Chose the same as "name"
    version='0.5.0',
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='Convert ofx + xlsx to xlsx - pt_BR',  # Give a short description about your library
    author='Fintask',  # Type in your name
    author_email='admin@fintask.com.br',  # Type in your E-Mail
    url='https://github.com/Fintask/ofxReaderBR/',  # Provide either the link to your github or to your website
    download_url='https://github.com/Fintask/ofxReaderBR/archive/v0.5.0.tar.gz',
    keywords=['ofx', 'xlsx'],  # Keywords that define your package best
    install_requires=[  # I get to this in a second
        'et-xmlfile',
        'jdcal',
        'openpyxl',
        'ofxtoolslambda',
        'pytz',
        'lxml',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package

        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',  # Again, pick a license

        'Programming Language :: Python :: 3.7',  # Specify which pyhton versions that you want to support
    ],
)
