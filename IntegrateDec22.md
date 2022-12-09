# Attempt to integrate in December 2022

## Resynchronize with `origin/master`
	1. synchronized by githup
	1. synchronized my local files
	  - fetched / pulled into master
	  - created new branch `AL-master4merge` for trying (brutal) merge with my changes 

    1. to list differences at time of PR (June 2021)
	
>	git diff 9F7C35 C29643 --name-status
>	9F7C35: their changes
>	C29643: my PR

Not as bad as it looks (changes in dpath/*.py are the real features)

>   git diff 9F7C35 C29643 --name-status 
>   A       .github/workflows/linterTest.yml
>   A       .github/workflows/python3-pypy-Test.yml
>   A       .github/workflows/python3Test.yml
>   M       .gitignore
>   M       .travis.yml
>   M       MAINTAINERS.md
>   M       README.rst
>   M       dpath/options.py
>   M       dpath/segments.py
>   M       dpath/util.py
>   M       dpath/version.py
>   A       issues/err_walk.py
>   A       maintainers_log.md
>   A       nose2.cfg
>   A       requirements-2.7.txt
>   A       requirements.txt
>   A       tests/test_path_ext.py
>   M       tests/test_segments.py
>   M       tests/test_unicode.py
>   M       tests/test_util_get_values.py
>   M       tox.ini


## 
