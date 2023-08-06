holdouts_generator
=========================================================================================
|travis| |sonar_quality| |sonar_maintainability| |codacy| |code_climate_maintainability| |pip| |downloads|

Simple python package to generate and cache both random and chromosomal holdouts with arbitrary depth.

How do I install this package?
----------------------------------------------
As usual, just download it using pip:

.. code:: shell

    pip install holdouts_generator

Tests Coverage
----------------------------------------------
Since some software handling coverages sometime get slightly different results, here's three of them:

|coveralls| |sonar_coverage| |code_climate_coverage|

Generating random holdouts
---------------------------------
Suppose you want to generate 3 layers of holdouts, respectively with 0.3, 0.2 and 0.1 as test size and 5, 3 and  2 as quantity:

.. code:: python

    from holdouts_generator import holdouts_generator, random_holdouts
    dataset = pd.read_csv("path/to/my/dataset.csv")
    generator = holdouts_generator(
        dataset,
        holdouts=random_holdouts(
            [0.3, 0.2, 0.1],
            [5, 3, 2]
        )
    )
    
    for (training, testing), inner_holdouts in generator():
        for (inner_train, inner_test), small_holdouts in inner_holdouts():
            for (small_train, small_test), _ in small_holdouts():
                #do what you need :)

Generating balanced random holdouts
-------------------------------------------------------
Suppose you want to generate 3 layers of holdouts, as above, but now you want to enforce to apply the same proportions for each class.
In this setup, it is of foundamental importance to pass the list of classes as the last argument.

.. code:: python

    from holdouts_generator import holdouts_generator, balanced_random_holdouts
    dataset = pd.read_csv("path/to/my/dataset.csv")
    classes = pd.read_csv("path/to/my/classes.csv")
    generator = holdouts_generator(
        dataset, classes,
        holdouts=balanced_random_holdouts(
            [0.3, 0.2, 0.1],
            [5, 3, 2]
        )
    )
    
    for (training, testing), inner_holdouts in generator():
        for (inner_train, inner_test), small_holdouts in inner_holdouts():
            for (small_train, small_test), _ in small_holdouts():
                #do what you need :)

Generating chromosomal holdouts
---------------------------------
Suppose you want to generate 2 layers of holdouts, two outer ones with chromosomes 17 and 18 and 3 inner ones, with chromosomes 17/18, 20 and 21:

.. code:: python

    from holdouts_generator import holdouts_generator, chromosomal_holdouts
    dataset = pd.read_csv("path/to/my/genomic_dataset.csv")
    generator = holdouts_generator(
        dataset,
        holdouts=chromosomal_holdouts([
            ([17], [([18], None), ([20], None), ([21], None)])
            ([18], [([17], None), ([20], None), ([21], None)])
        ])
    )

    for (training, testing), inner_holdouts in generator():
        for (inner_train, inner_test), _ in inner_holdouts():
            #do what you need :)

Generating cached holdouts
---------------------------------
To generate a cached holdout you just need to import instead of holdouts_generator the other method called cached_holdouts_generator.
Everything else stays basically the same, except you receive also the holdout cached key for storing the results.

.. code:: python

    from holdouts_generator import cached_holdouts_generator, balanced_random_holdouts
    dataset = pd.read_csv("path/to/my/dataset.csv")
    classes = pd.read_csv("path/to/my/classes.csv")
    generator = cached_holdouts_generator(
        dataset, classes,
        holdouts=balanced_random_holdouts(
            [0.3, 0.2],
            [5, 3]
        )
    )
    
    for (training, testing), key, inner_holdouts in generator():
        for (inner_train, inner_test), inner_key, small_holdouts in inner_holdouts():
            #do what you need :)

Clearing the holdouts cache
--------------------------------------
Just run the method `clear_cache`:

.. code:: python

    from holdouts_generator import clear_cache

    clear_cache(
        cache_dir=".holdouts" # This is the default cache directory
    )

Clearing the invalid holdouts
--------------------------------------
Sometimes it can happen that by moving around holdouts or
simply by running parallel processes on clusters with machine with different specifics
some holdouts can be created twice, overriding the original cache.

In this unlikely scenario, the holdouts will be marked as **tempered**.
To delete these holdouts use the following:

.. code:: python

    from holdouts_generator import clear_invalid_cache

    clear_invalid_cache(
        cache_dir=".holdouts" # This is the default cache directory
    )


Clearing the invalid results
--------------------------------------
As you can get invalid holdouts, it is also possible to get invalid results that map
to invalid holduts. For this reason there is a method to delete these results:

.. code:: python

    from holdouts_generator import clear_invalid_results

    clear_invalid_results(
        results_directory: str = "results", # This is the default results directory
        cache_dir=".holdouts" # This is the default cache directory
    )

.. |travis| image:: https://travis-ci.org/LucaCappelletti94/holdouts_generator.png
   :target: https://travis-ci.org/LucaCappelletti94/holdouts_generator
   :alt: Travis CI build

.. |sonar_quality| image:: https://sonarcloud.io/api/project_badges/measure?project=LucaCappelletti94_holdouts_generator&metric=alert_status
    :target: https://sonarcloud.io/dashboard/index/LucaCappelletti94_holdouts_generator
    :alt: SonarCloud Quality

.. |sonar_maintainability| image:: https://sonarcloud.io/api/project_badges/measure?project=LucaCappelletti94_holdouts_generator&metric=sqale_rating
    :target: https://sonarcloud.io/dashboard/index/LucaCappelletti94_holdouts_generator
    :alt: SonarCloud Maintainability

.. |sonar_coverage| image:: https://sonarcloud.io/api/project_badges/measure?project=LucaCappelletti94_holdouts_generator&metric=coverage
    :target: https://sonarcloud.io/dashboard/index/LucaCappelletti94_holdouts_generator
    :alt: SonarCloud Coverage

.. |coveralls| image:: https://coveralls.io/repos/github/LucaCappelletti94/holdouts_generator/badge.svg?branch=master
    :target: https://coveralls.io/github/LucaCappelletti94/holdouts_generator?branch=master
    :alt: Coveralls Coverage

.. |pip| image:: https://badge.fury.io/py/holdouts-generator.svg
    :target: https://badge.fury.io/py/holdouts-generator
    :alt: Pypi project

.. |downloads| image:: https://pepy.tech/badge/holdouts-generator
    :target: https://pepy.tech/badge/holdouts-generator
    :alt: Pypi total project downloads 

.. |codacy|  image:: https://api.codacy.com/project/badge/Grade/31638d8f26b0487184573515c46af276
    :target: https://www.codacy.com/app/LucaCappelletti94/holdouts_generator?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=LucaCappelletti94/holdouts_generator&amp;utm_campaign=Badge_Grade
    :alt: Codacy Maintainability

.. |code_climate_maintainability| image:: https://api.codeclimate.com/v1/badges/676d2d50c7980eeaa00c/maintainability
    :target: https://codeclimate.com/github/LucaCappelletti94/holdouts_generator/maintainability
    :alt: Maintainability

.. |code_climate_coverage| image:: https://api.codeclimate.com/v1/badges/676d2d50c7980eeaa00c/test_coverage
    :target: https://codeclimate.com/github/LucaCappelletti94/holdouts_generator/test_coverage
    :alt: Code Climate Coverate