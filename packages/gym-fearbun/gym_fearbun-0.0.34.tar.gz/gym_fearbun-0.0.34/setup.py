from setuptools import setup
from Cython.Build import cythonize
import setuptools

setup(name='gym_fearbun',
      version='0.0.34',
      install_requires=['gym', 'six', 'Cython', 'numpy'],
      url='https://github.com/rolypolyvg295/gym_fearbun/tree/master/gym_fearbun',
      include_package_data=True,
      packages=setuptools.find_packages(),
      package_data={'gym_fearbun/envs/raceboard/maps': ['*.txt']},
      license='MIT',
      ext_modules=cythonize(['gym_fearbun/envs/raceboard/c_raceboard.pyx', 'chapter_5/cother_agent.pyx'],
                            compiler_directives={'language_level': 3},
                            annotate=True)
      )
